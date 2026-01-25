"""Launch the FastAPI backend used by the React frontend."""

import uvicorn


def main():
    uvicorn.run(
        "backend.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
