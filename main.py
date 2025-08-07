import meta_api

def main():
    """
    Main function to run the Facebook Ad creation tool.
    """
    print("--- Facebook Ad Creator ---")
    try:
        meta_api.initialize_api()
        print("API initialized successfully.")

        # In the future, this will be replaced with a CLI
        # to gather campaign details from the user.

        # Get campaign details from the user via CLI
        name, objective, status = get_campaign_details_from_user()

        # Confirm before creating
        print("\n--- Campaign Summary ---")
        print(f"  Name:      {name}")
        print(f"  Objective: {objective}")
        print(f"  Status:    {status}")

        confirm = input("\nDo you want to create this campaign? (yes/no): ").lower()

        if confirm in ['yes', 'y']:
            print("\nAttempting to create the campaign...")
            ad_account = meta_api.get_ad_account()
            meta_api.create_campaign(
                ad_account=ad_account,
                name=name,
                objective=objective,
                status=status
            )
        else:
            print("Campaign creation cancelled.")

    except FileNotFoundError:
        print("\nERROR: config.ini not found.")
        print("Please copy config.ini.template to config.ini and fill in your credentials.")
    except KeyError as e:
        print(f"ERROR: Missing configuration key: {e}")
        print("Please make sure your config.ini file is complete.")

def get_campaign_details_from_user():
    """Prompts the user for campaign details and returns them."""

    # 1. Get Campaign Name
    name = input("Enter the campaign name: ")
    while not name:
        print("Campaign name cannot be empty.")
        name = input("Enter the campaign name: ")

    # 2. Get Campaign Objective
    print("\nSelect a campaign objective:")
    objectives = {
        '1': 'LINK_CLICKS',
        '2': 'CONVERSIONS',
        '3': 'POST_ENGAGEMENT',
        '4': 'LEAD_GENERATION',
        '5': 'OUTCOME_SALES',
        '6': 'OUTCOME_TRAFFIC',
    }
    for key, value in objectives.items():
        print(f"  {key}: {value}")

    objective_choice = ''
    while objective_choice not in objectives:
        objective_choice = input(f"Enter the number for your objective (1-{len(objectives)}): ")
        if objective_choice not in objectives:
            print("Invalid choice. Please select a number from the list.")
    objective = objectives[objective_choice]

    # 3. Get Campaign Status
    status = ''
    while status not in ['ACTIVE', 'PAUSED']:
        status_choice = input("\nSet campaign status to ACTIVE or PAUSED? [PAUSED]: ").upper()
        if not status_choice:
            status = 'PAUSED'
        elif status_choice in ['ACTIVE', 'PAUSED']:
            status = status_choice
        else:
            print("Invalid status. Please choose ACTIVE or PAUSED.")

    return name, objective, status

if __name__ == "__main__":
    main()
