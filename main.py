from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/run-monthly-playlist")
def run_playlist():
    result = subprocess.run(
        ["python3", "monthly_playlist.py"],
        capture_output=True,
        text=True
    )

    print("===== MONTHLY PLAYLIST SCRIPT OUTPUT =====")
    print(result.stdout)
    if result.stderr:
        print("===== ERRORS =====")
        print(result.stderr)

    return {
        "status": "success" if result.returncode == 0 else "error",
        "stdout": result.stdout,
        "stderr": result.stderr
    }
