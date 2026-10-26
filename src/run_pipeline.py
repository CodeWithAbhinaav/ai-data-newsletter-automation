
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_FOLDER = PROJECT_ROOT / "src"


# --------------------------------------------------
# 2. PIPELINE CONFIGURATION
# --------------------------------------------------

PIPELINE_STAGES = [
    {
        "name": "Collect Databricks RSS feed",
        "script": "collect_databricks_feed.py",
    },
    {
        "name": "Filter articles by date",
        "script": "filter_recent_articles.py",
    },
    {
        "name": "Clean duplicate articles",
        "script": "clean_articles.py",
    },
    {
        "name": "Rank articles",
        "script": "rank_articles.py",
    },
    {
        "name": "Select newsletter shortlist",
        "script": "select_newsletter_articles.py",
    },
    {
        "name": "Generate Markdown newsletter",
        "script": "generate_newsletter.py",
    },
    {
        "name": "Generate newsletter PDF",
        "script": "generate_newsletter_pdf.py",
    },
]


# --------------------------------------------------
# 3. DISPLAY HELPERS
# --------------------------------------------------

def print_header():
    print("\n" + "=" * 65)
    print("       AI & DATA NEWSLETTER AUTOMATION PIPELINE")
    print("=" * 65)
    print(f"Project folder : {PROJECT_ROOT}")
    print(f"Python version : {sys.version.split()[0]}")
    print(f"Started at     : {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Total stages   : {len(PIPELINE_STAGES)}")
    print("=" * 65)


def print_stage_header(stage_number, total_stages, stage_name):
    print("\n")
    print("-" * 65)
    print(f"STAGE {stage_number}/{total_stages}: {stage_name}")
    print("-" * 65)


# --------------------------------------------------
# 4. CHECK REQUIRED SCRIPTS BEFORE RUNNING
# --------------------------------------------------

def validate_scripts():
    missing_scripts = []

    for stage in PIPELINE_STAGES:
        script_path = SRC_FOLDER / stage["script"]

        if not script_path.is_file():
            missing_scripts.append(script_path)

    if missing_scripts:
        print("\nERROR: The following required scripts were not found:")

        for path in missing_scripts:
            print(f"  - {path}")

        print("\nCheck the filenames and make sure all seven scripts")
        print("are saved inside your project's src folder.")

        return False

    return True


# --------------------------------------------------
# 5. RUN ONE PIPELINE STAGE
# --------------------------------------------------

def run_stage(stage_number, total_stages, stage):
    stage_name = stage["name"]
    script_path = SRC_FOLDER / stage["script"]

    print_stage_header(stage_number, total_stages, stage_name)
    print(f"Script: {script_path.name}")
    print(f"Using Python: {sys.executable}\n")

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=False,
        )

    except KeyboardInterrupt:
        elapsed = time.perf_counter() - start_time

        print(f"\nStage interrupted by user: {stage_name}")
        print(f"Time before interruption: {elapsed:.1f} seconds")

        raise

    except OSError as error:
        elapsed = time.perf_counter() - start_time

        print(f"\nERROR: Could not start {script_path.name}")
        print(f"Details: {error}")
        print(f"Time elapsed: {elapsed:.1f} seconds")

        return False, elapsed, "Could not start script"

    elapsed = time.perf_counter() - start_time

    if result.returncode != 0:
        print(f"\nFAILED: {stage_name}")
        print(f"Exit code: {result.returncode}")
        print(f"Time elapsed: {elapsed:.1f} seconds")

        return False, elapsed, f"Exit code {result.returncode}"

    print(f"\nSUCCESS: {stage_name}")
    print(f"Time elapsed: {elapsed:.1f} seconds")

    return True, elapsed, "Success"


# --------------------------------------------------
# 6. DISPLAY FINAL SUMMARY
# --------------------------------------------------

def print_summary(results, total_elapsed):
    print("\n\n" + "=" * 65)
    print("                 PIPELINE SUMMARY")
    print("=" * 65)

    successful = sum(
        1 for result in results
        if result["status"] == "SUCCESS"
    )

    failed = sum(
        1 for result in results
        if result["status"] == "FAILED"
    )

    for result in results:
        print(
            f'{result["number"]}. {result["name"]}'
            f' — {result["status"]}'
            f' ({result["elapsed"]:.1f}s)'
        )

        if result["status"] == "FAILED":
            print(f'   Reason: {result["reason"]}')

    print("-" * 65)
    print(f"Successful stages: {successful}/{len(PIPELINE_STAGES)}")
    print(f"Failed stages    : {failed}")
    print(f"Total runtime    : {total_elapsed:.1f} seconds")

    if failed == 0 and successful == len(PIPELINE_STAGES):
        print("\nPIPELINE COMPLETED SUCCESSFULLY!")
        print("\nExpected final outputs:")

        print(
            "  Markdown: data/processed/"
            "databricks_newsletter_draft.md"
        )
        print(
            "  PDF     : data/processed/"
            "databricks_newsletter.pdf"
        )

        print(
            "\nPlease review the newsletter before publishing."
        )
    else:
        print("\nPIPELINE DID NOT COMPLETE.")
        print("Fix the failed stage before attempting another run.")

    print("=" * 65)


# --------------------------------------------------
# 7. MAIN PIPELINE
# --------------------------------------------------

def main():
    print_header()

    if not validate_scripts():
        sys.exit(1)

    results = []
    pipeline_start = time.perf_counter()

    for number, stage in enumerate(PIPELINE_STAGES, start=1):
        success, elapsed, reason = run_stage(
            number,
            len(PIPELINE_STAGES),
            stage,
        )

        results.append(
            {
                "number": number,
                "name": stage["name"],
                "status": "SUCCESS" if success else "FAILED",
                "elapsed": elapsed,
                "reason": reason,
            }
        )

        # Stop immediately if a stage fails.
        if not success:
            break

    total_elapsed = time.perf_counter() - pipeline_start
    print_summary(results, total_elapsed)

    if len(results) != len(PIPELINE_STAGES):
        print(
            "\nRemaining stages were skipped because an earlier "
            "stage failed."
        )

    if any(result["status"] == "FAILED" for result in results):
        sys.exit(1)


# --------------------------------------------------
# 8. SCRIPT ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPipeline stopped by user.")
        sys.exit(130)
