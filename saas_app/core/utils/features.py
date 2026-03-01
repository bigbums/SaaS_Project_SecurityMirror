# core/utils/features.py
def has_feature(user, feature_name):
    """
    Checks if a user has access to a given feature.
    This could be based on role, subscription plan, or flags.
    """
    # Example logic: check user's plan or role
    if hasattr(user, "plan") and feature_name in user.plan.features:
        return True
    if hasattr(user, "role") and feature_name in user.role.allowed_features:
        return True
    return False
