import threading
import webbrowser

from app import create_app


def main() -> None:
    port = 8839
    local_url = f"http://127.0.0.1:{port}"

    app = create_app()

    threading.Timer(1.0, lambda: webbrowser.open(local_url)).start()

    print("Kinh Dich App is running.")
    print(f"  - Open in browser: {local_url}")
    print()
    print("Close this window (or press Ctrl+C) to stop the app.")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
