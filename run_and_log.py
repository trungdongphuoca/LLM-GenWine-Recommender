"""
run_and_log.py
==============
Chạy toàn bộ pipeline đánh giá và ghi log có timestamp đầy đủ.
Log được lưu tại results/run_logs/ để thầy hướng dẫn xác thực số liệu.
"""
import sys, os, json, time, datetime, platform, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "run_logs")
os.makedirs(LOG_DIR, exist_ok=True)

RUN_TS  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"run_{RUN_TS}.log")

class Tee:
    """Redirect stdout to both console and log file simultaneously."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

def get_env_info():
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "hostname": platform.node(),
        "seed": 42,
    }
    try:
        import torch
        info["cuda_available"] = torch.cuda.is_available()
        info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"
        info["torch_version"] = torch.__version__
    except ImportError:
        info["cuda_available"] = False
    return info

def run_script(script_path, label):
    print(f"\n{'='*60}")
    print(f"[{label}] Starting: {script_path}")
    print(f"[{label}] Time: {datetime.datetime.now().isoformat()}")
    print(f"{'='*60}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "-X", "utf8", script_path],
        capture_output=True, text=True, encoding='utf-8'
    )
    elapsed = time.time() - t0
    print(result.stdout)
    if result.stderr:
        print("[STDERR]:", result.stderr[:2000])
    print(f"[{label}] Completed in {elapsed:.1f}s — exit code: {result.returncode}")
    return {"label": label, "elapsed_sec": round(elapsed, 2), "returncode": result.returncode}

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as log_f:
        sys.stdout = Tee(sys.__stdout__, log_f)

        print("=" * 70)
        print("  EXPERIMENT RUN LOG")
        print(f"  Project: LLM-GenWine-Recommender (Chuyen de 3)")
        print(f"  Run ID : {RUN_TS}")
        print("=" * 70)

        env = get_env_info()
        print("\n[ENVIRONMENT]")
        for k, v in env.items():
            print(f"  {k}: {v}")

        scripts = [
            ("evaluation/baseline_eval.py",          "Baseline Evaluation (BM25/TF-IDF)"),
            ("evaluation/noisy_query_benchmark.py",   "Noisy Query Benchmark"),
        ]

        results = []
        for script, label in scripts:
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
            if os.path.exists(full_path):
                r = run_script(full_path, label)
                results.append(r)
            else:
                print(f"[WARNING] Script not found: {full_path}")

        print("\n" + "=" * 70)
        print("  SUMMARY")
        print("=" * 70)
        for r in results:
            status = "OK" if r["returncode"] == 0 else "FAILED"
            print(f"  [{status}] {r['label']:45s}  {r['elapsed_sec']:6.1f}s")

        # Save run metadata as JSON
        meta_path = os.path.join(LOG_DIR, f"run_{RUN_TS}_meta.json")
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump({"env": env, "scripts": results, "log_file": LOG_FILE}, mf, indent=2, ensure_ascii=False)
        print(f"\n[LOG] Saved to: {LOG_FILE}")
        print(f"[META] Saved to: {meta_path}")
        sys.stdout = sys.__stdout__
