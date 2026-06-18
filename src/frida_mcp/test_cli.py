#!/usr/bin/env python3
"""
Test script for the functions defined in src/frida_mcp/cli.py.
This script demonstrates basic calls to each exported function.
Many functions interact with Frida devices/processes and therefore may require a
connected device or a running process. The script catches exceptions and prints
the results, so it can be run safely even when the required environment is not
available.
"""

import sys
import traceback
from typing import Any, List, Dict

# Import the functions from the CLI module
try:
    from frida_mcp.cli import (
        connect_to_device,
        enumerate_processes,
        enumerate_devices,
        get_device,
        get_usb_device,
        get_local_device,
        get_process_by_name,
        attach_to_process,
        spawn_process,
        resume_process,
        kill_process,
        get_version,
        get_processes_resource,
        get_devices_resource,
        create_interactive_session,
        execute_in_session,
        get_session_messages,
    )
except Exception as e:
    print("Failed to import functions from frida_mcp.cli:", e)
    sys.exit(1)


def safe_call(name: str, func, *args, **kwargs) -> None:
    """Execute a function, printing its result or any raised exception.

    Args:
        name: Human‑readable name of the operation.
        func: Callable to invoke.
        *args: Positional arguments for the callable.
        **kwargs: Keyword arguments for the callable.
    """
    print(f"\n=== {name} ===")
    try:
        result = func(*args, **kwargs)
        print("Result:", result)
    except Exception as exc:
        print("Exception raised:")
        traceback.print_exc()


def test_all() -> None:
    # 1. Connect to a remote device (example host – replace with a real one if needed)
    safe_call(
        "connect_to_device",
        connect_to_device,
        host="127.0.0.1:27042",
    )

    # 2. Enumerate devices
    safe_call("enumerate_devices", enumerate_devices)

    # 3. Enumerate processes on the default (USB) device
    safe_call("enumerate_processes", enumerate_processes)

    # 4. Get a specific device – using the first device from enumerate_devices if any
    devices = enumerate_devices()
    if devices:
        first_id = devices[0].get("id")
        safe_call("get_device", get_device, device_id=first_id)
    else:
        print("No devices found – skipping get_device test.")

    # 5. Get USB device info
    safe_call("get_usb_device", get_usb_device)

    # 6. Get local device info
    safe_call("get_local_device", get_local_device)

    # 7. Find a process by name – using a common system process name as example
    safe_call(
        "get_process_by_name",
        get_process_by_name,
        name="explorer",  # Windows explorer; adjust for other OSes
    )

    # 8. Attach to a process – this requires a valid PID; we attempt with the PID from the previous call if found
    proc_info = get_process_by_name(name="explorer")
    if proc_info.get("found"):
        pid = proc_info.get("pid")
        safe_call("attach_to_process", attach_to_process, pid=pid)
    else:
        print("Process 'explorer' not found – skipping attach_to_process test.")

    # 9. Spawn a process – example using notepad on Windows
    safe_call(
        "spawn_process",
        spawn_process,
        program="notepad.exe",
        args=[],
    )

    # 10. Resume a process – using the PID from spawn_process if successful
    spawn_result = spawn_process(program="notepad.exe", args=[])
    if isinstance(spawn_result, dict) and "pid" in spawn_result:
        pid = spawn_result["pid"]
        safe_call("resume_process", resume_process, pid=pid)
    else:
        print("Spawned process info not available – skipping resume_process test.")

    # 11. Kill a process – using the same PID (be careful when running this script!)
    if isinstance(spawn_result, dict) and "pid" in spawn_result:
        pid = spawn_result["pid"]
        safe_call("kill_process", kill_process, pid=pid)
    else:
        print("No PID to kill – skipping kill_process test.")

    # 12. Get Frida version
    safe_call("get_version", get_version)

    # 13. Get processes resource (string representation)
    safe_call("get_processes_resource", get_processes_resource)

    # 14. Get devices resource (string representation)
    safe_call("get_devices_resource", get_devices_resource)

    # 15. Create an interactive session – requires a running process PID
    # We'll reuse the PID from spawn_process if it exists.
    if isinstance(spawn_result, dict) and "pid" in spawn_result:
        pid = spawn_result["pid"]
        session_info = create_interactive_session(process_id=pid)
        safe_call("create_interactive_session", lambda: session_info)
        if session_info.get("status") == "success":
            session_id = session_info.get("session_id")
            # 16. Execute a simple JavaScript snippet in the session
            safe_call(
                "execute_in_session",
                execute_in_session,
                session_id=session_id,
                javascript_code="'Hello from Frida';",
                keep_alive=False,
            )
            # 17. Retrieve any session messages (should be empty for non‑persistent script)
            safe_call("get_session_messages", get_session_messages, session_id=session_id)
        else:
            print("Interactive session creation failed – skipping script execution tests.")
    else:
        print("No PID available for interactive session – skipping related tests.")


if __name__ == "__main__":
    test_all()
