"""
run_and_log.py
==============
Chạy TOÀN BỘ pipeline đánh giá trên GPU và ghi log đầy đủ.
Log lưu tại results/run_logs/ để thầy hướng dẫn xác thực số liệu báo cáo.

Pipeline thứ tự chạy:
  1. Baseline Eval        — BM25, TF-IDF, GNN, Struct-Filter (N=12,991)
  2. Model 1 (TIGER)      — Constrained Beam Search + Price Rerank (N=500 mock)
  3. Model 2 (Parser)     — LLM Parser → Struct Filter → Sommelier (N=12,991)
  4. Ablation Study       — 5 biến thể thành phần của Mô hình 1
  5. Cluster Eval         — Phân tích Cluster Match@1
  6. Noisy Benchmark      — 100 query nhiễu (3 danh mục)

Usage:
    python run_and_log.py              # chạy tất cả
    python run_and_log.py --baseline   # chỉ chạy baseline
    python run_and_log.py --noisy      # chỉ chạy noisy benchmark
    python run_and_log.py --model1     # chỉ chạy Model 1
    python run_and_log.py --model2     # chỉ chạy Model 2
    python run_and_log.py --ablation   # chỉ chạy ablation
"""
import sys, os, json, time, datetime, platform, subprocess, argparse

LOG_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "run_logs")
os.makedirs(LOG_DIR, exist_ok=True)
RUN_TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"run_{RUN_TS}.log")

# ── Argument parsing ─────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--baseline",  action="store_true")
parser.add_argument("--model1",    action="store_true")
parser.add_argument("--model2",    action="store_true")
parser.add_argument("--ablation",  action="store_true")
parser.add_argument("--cluster",   action="store_true")
parser.add_argument("--noisy",     action="store_true")
args = parser.parse_args()
run_all = not any([args.baseline, args.model1, args.model2,
                   args.ablation, args.cluster, args.noisy])

# ── Tee logger ───────────────────────────────────────────────────────────────
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj); f.flush()
    def flush(self):
        for f in self.files: f.flush()

# ── Environment info ─────────────────────────────────────────────────────────
def get_env_info():
    info = {
        "run_id"    : RUN_TS,
        "timestamp" : datetime.datetime.now().isoformat(),
        "platform"  : platform.platform(),
        "python"    : sys.version.split("\n")[0],
        "hostname"  : platform.node(),
        "seed"      : 42,
    }
    try:
        import torch
        info["torch"]          = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            info["gpu"]        = props.name
            info["vram_gb"]    = round(props.total_memory / 1e9, 1)
            info["cuda"]       = torch.version.cuda
        else:
            info["gpu"]        = "CPU only"
    except ImportError:
        info["cuda_available"] = False
        info["gpu"]            = "PyTorch not installed"
    return info

# ── Run one script ────────────────────────────────────────────────────────────
def run_script(script_path, label, extra_args=None, use_gpu=True):
    print(f"\n{'='*65}")
    print(f"  STEP : {label}")
    print(f"  File : {os.path.basename(script_path)}")
    print(f"  Time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  GPU  : {'CUDA:0' if use_gpu else 'CPU'}")
    print(f"{'='*65}")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["CUDA_VISIBLE_DEVICES"] = "0" if use_gpu else ""

    cmd = [sys.executable, "-X", "utf8", script_path] + (extra_args or [])
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8", env=env)
    elapsed = time.time() - t0

    # Print stdout
    if result.stdout.strip():
        print(result.stdout)

    # Print stderr — skip tqdm progress lines
    if result.stderr:
        lines = [l for l in result.stderr.splitlines()
                 if not any(x in l for x in ["it/s", "█", "%|", "ETA"])]
        filtered = "\n".join(lines[:40])
        if filtered.strip():
            print(f"[STDERR]\n{filtered}")

    status = "OK" if result.returncode == 0 else "FAILED"
    print(f"\n  → {status} in {elapsed:.1f}s (exit {result.returncode})")
    return {"label": label, "script": os.path.basename(script_path),
            "elapsed_sec": round(elapsed, 2), "returncode": result.returncode,
            "status": status}

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.abspath(__file__))
    EVAL = os.path.join(ROOT, "evaluation")

    with open(LOG_FILE, "w", encoding="utf-8") as log_f:
        sys.stdout = Tee(sys.__stdout__, log_f)

        print("=" * 65)
        print("  EXPERIMENT RUN LOG")
        print("  Project : LLM-GenWine-Recommender — Chuyen de 3")
        print(f"  Run ID  : {RUN_TS}")
        print(f"  Log     : {LOG_FILE}")
        print("=" * 65)

        env = get_env_info()
        print("\n[ENVIRONMENT]")
        for k, v in env.items():
            print(f"  {k:<20}: {v}")

        try:
            import torch
            has_gpu = torch.cuda.is_available()
        except ImportError:
            has_gpu = False

        print(f"\n  → Compute: {'GPU (' + env.get('gpu','') + ', ' + str(env.get('vram_gb','')) + 'GB)' if has_gpu else 'CPU'}")
        print(f"  → CUDA   : {env.get('cuda', 'N/A')}")

        # ── Define all scripts ───────────────────────────────────────────────
        ALL_STEPS = [
            {
                "key"   : "baseline",
                "label" : "Step 1 — Baseline Eval (BM25/TF-IDF/GNN/Struct-Filter, N=12991)",
                "script": os.path.join(EVAL, "baseline_eval.py"),
                "args"  : [],
                "gpu"   : has_gpu,
            },
            {
                "key"   : "model1",
                "label" : "Step 2 — Model 1: TIGER + Constrained Beam Search + Price Rerank",
                "script": os.path.join(EVAL, "constrained_eval.py"),
                "args"  : ["--num_beams", "10", "--num_return_sequences", "10", "--eval_size", "500", "--mock"],
                "gpu"   : has_gpu,
            },
            {
                "key"   : "model2",
                "label" : "Step 3 — Model 2: LLM Parser → Struct Filter → Sommelier (N=12991)",
                "script": os.path.join(EVAL, "eval_model2_full.py"),
                "args"  : [],
                "gpu"   : has_gpu,
            },
            {
                "key"   : "ablation",
                "label" : "Step 4 — Ablation Study (5 variants of Model 1)",
                "script": os.path.join(EVAL, "ablation_eval.py"),
                "args"  : [],
                "gpu"   : has_gpu,
            },
            {
                "key"   : "cluster",
                "label" : "Step 5 — Cluster Match Analysis (Valid-ID Rate, Cluster Match@1)",
                "script": os.path.join(EVAL, "cluster_eval.py"),
                "args"  : [],
                "gpu"   : has_gpu,
            },
            {
                "key"   : "noisy",
                "label" : "Step 6 — Noisy Query Benchmark (N=100, 3 categories)",
                "script": os.path.join(EVAL, "noisy_query_benchmark.py"),
                "args"  : [],
                "gpu"   : has_gpu,
            },
        ]

        # ── Filter which steps to run ────────────────────────────────────────
        steps = [s for s in ALL_STEPS
                 if run_all or getattr(args, s["key"], False)]

        print(f"\n  → Running {len(steps)}/{len(ALL_STEPS)} steps\n")

        # ── Execute ──────────────────────────────────────────────────────────
        results = []
        for step in steps:
            if os.path.exists(step["script"]):
                r = run_script(step["script"], step["label"],
                               extra_args=step["args"], use_gpu=step["gpu"])
                results.append(r)
            else:
                print(f"\n[SKIP] Not found: {step['script']}")
                results.append({"label": step["label"], "status": "SKIPPED",
                                 "elapsed_sec": 0, "returncode": -1})

        # ── Summary ───────────────────────────────────────────────────────────
        print("\n" + "=" * 65)
        print("  FINAL SUMMARY")
        print("=" * 65)
        all_ok = True
        for r in results:
            icon = {"OK": "✅", "FAILED": "❌", "SKIPPED": "⏭️"}.get(r["status"], "?")
            print(f"  {icon} [{r['status']:<7}] {r['label'][:52]:<52}  {r['elapsed_sec']:7.1f}s")
            if r["status"] == "FAILED":
                all_ok = False

        total = sum(r["elapsed_sec"] for r in results)
        print(f"\n  Total time : {total/60:.1f} min")
        print(f"  Result     : {'ALL PASSED ✅' if all_ok else 'SOME FAILED ❌'}")
        print(f"  Log saved  : {LOG_FILE}")

        # ── Save JSON metadata ────────────────────────────────────────────────
        meta = {"env": env, "steps": results, "log_file": LOG_FILE,
                "all_ok": all_ok, "total_sec": round(total, 1)}
        meta_path = LOG_FILE.replace(".log", "_meta.json")
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, indent=2, ensure_ascii=False)
        print(f"  Meta saved : {meta_path}")

        sys.stdout = sys.__stdout__

    print(f"\n[DONE] Full run complete. Log: {LOG_FILE}")
