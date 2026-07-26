# Demo Reset Runbook

If you need to reset the system between rehearsals or judging rounds, follow these steps:

1. **Stop the Backend**: `Ctrl+C` the FastAPI terminal.
2. **Clear the Event Store**: Delete `events.sqlite` in the `data/` folder.
    ```bash
    rm data/events.sqlite
    ```
3. **Restart the Backend**:
    ```bash
    uvicorn apps.api.main:app --reload
    ```
4. **Refresh the Dashboard**: Hit `F5` on the browser to clear the React state and reload the fresh baseline data.
