from activity_monitor import ActivityMonitor


def main():
    monitor = ActivityMonitor(check_interval=10)  # Adjust check_interval for testing
    try:
        monitor.start()
        input("Monitoring... Press Enter to stop.\n")  # Let it run until user stops it
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
