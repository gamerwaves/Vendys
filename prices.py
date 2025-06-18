import math

def calculate_normal_points(whole_dollars):
    if whole_dollars == 1:
        return 5
    elif whole_dollars == 2:
        return 11
    elif whole_dollars >= 3:
        return 13 + 2 * (whole_dollars - 3)
    else:
        return 0

def calculate_premium_points(whole_dollars):
    if whole_dollars == 1:
        return 2
    elif whole_dollars == 2:
        return 5
    elif whole_dollars >= 3:
        return 6 + 1 * (whole_dollars - 3)
    else:
        return 0

def calculate_points(dollars):
    if dollars < 1:
        return (0, 0)

    whole_dollars = math.floor(dollars)
    fraction = dollars - whole_dollars

    # Normal points
    norm_points = calculate_normal_points(whole_dollars)
    next_norm = calculate_normal_points(whole_dollars + 1)
    norm_extra = (next_norm - norm_points) * fraction
    total_norm = norm_points + norm_extra

    # Premium points
    prem_points = calculate_premium_points(whole_dollars)
    next_prem = calculate_premium_points(whole_dollars + 1)
    prem_extra = (next_prem - prem_points) * fraction
    total_prem = prem_points + prem_extra

    return (round(total_norm), round(total_prem))

def main():
    try:
        dollars = float(input("Enter dollar amount: "))
        if dollars < 1:
            print("Dollar amount must be 1 or greater.")
        else:
            norm_points, prem_points = calculate_points(dollars)
            print(f"${dollars:.2f} earns:")
            print(f"  Normal points: {norm_points}")
            print(f"  Premium points: {prem_points}")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()


