#!/usr/bin/env python3
"""
Claude Auto Approver - Main Entry Point
Automatically handles approval prompts with intelligent pattern detection
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auto_approver import AutoApprover
from src.utils.config import load_config


def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('auto_approver.log')
        ]
    )


def main():
    """Main function"""
    print("🤖 Claude Auto Approver Starting...")
    print("-" * 50)

    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config.get('log_level', 'INFO'))
    logger = logging.getLogger(__name__)

    try:
        # Initialize the auto approver
        approver = AutoApprover(config)

        # Show menu
        while True:
            print("\n📋 Main Menu:")
            print("1. Start Auto Approval")
            print("2. Configure Settings")
            print("3. View Logs")
            print("4. Test Pattern Detection")
            print("5. Exit")

            choice = input("\nSelect option (1-5): ").strip()

            if choice == '1':
                print("\n✅ Starting auto approval...")
                approver.start()
                input("Press Enter to stop...")
                approver.stop()
                print("⏹️ Auto approval stopped.")

            elif choice == '2':
                print("\n⚙️ Current Settings:")
                for key, value in config.items():
                    print(f"  {key}: {value}")

            elif choice == '3':
                print("\n📄 Recent Logs:")
                with open('auto_approver.log', 'r') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:  # Show last 20 lines
                        print(line.strip())

            elif choice == '4':
                test_text = input("\nEnter text to test pattern matching: ")
                if approver.detect_pattern(test_text):
                    print("✅ Pattern matched!")
                else:
                    print("❌ No pattern match.")

            elif choice == '5':
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid option. Please try again.")

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user.")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")

    finally:
        print("\n🏁 Claude Auto Approver Exited.")


if __name__ == "__main__":
    main()