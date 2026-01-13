from fastapi import FastAPI, HTTPException
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

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=result.stderr or "Playlist script failed"
        )

    return {
        "status": "success",
        "output": result.stdout
    }

