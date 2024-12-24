def consume_credits(user, credits):
    user.reset_daily_limit()  # Ensure daily limit is up to date
    if not user.is_premium and user.credits_used_today + credits > user.daily_limit:
        raise ValueError("Daily credit limit exceeded.")
    
    user.credits_used_today += credits
    user.total_credits_used += credits
    user.save()
