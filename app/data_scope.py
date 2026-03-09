"""
Data scope filtering for users based on role and job_title.data_scope.

Rules:
- ADMIN role: full access (no filtering)
- Users in "BAN GIÁM ĐỐC" org_unit: full access but excludes ADMIN users
- data_scope == 'all': full access but excludes ADMIN users
  (e.g., GD_VP, PGD_VP can see all users except admins)
- data_scope == 'subtree': own org_unit + all descendants
- data_scope == 'unit': only same org_unit_id
- data_scope == 'self': only own user record
"""

from app.models import User, OrgUnit, UserRole


def get_org_unit_descendants(org_unit_id):
    """
    Get all descendant unit IDs (including self) for a given org_unit_id.
    Uses breadth-first search to handle multi-level hierarchies.
    
    Returns: set of org_unit_id integers
    """
    if org_unit_id is None:
        return set()
    
    unit_ids = {org_unit_id}
    frontier = {org_unit_id}
    
    while frontier:
        children = (
            OrgUnit.query.filter(OrgUnit.parent_id.in_(list(frontier)))
            .with_entities(OrgUnit.id)
            .all()
        )
        next_frontier = {c.id for c in children} - unit_ids
        if not next_frontier:
            break
        unit_ids.update(next_frontier)
        frontier = next_frontier
    
    return unit_ids


def apply_user_scope(query, current_user):
    """
    Apply data scope filtering to a User query based on current_user's role
    and job_title.data_scope.
    
    Args:
        query: SQLAlchemy User query object
        current_user: User object (with job_title_ref relationship loaded)
    
    Returns:
        Filtered SQLAlchemy query
    """
    if current_user is None:
        return query
    
    # ADMIN has full access
    if current_user.role == UserRole.ADMIN:
        return query
    
    # Special case: Users in "BAN GIÁM ĐỐC" have full access except admin
    if current_user.org_unit and current_user.org_unit.name == "BAN GIÁM ĐỐC":
        return query.filter(User.role != UserRole.ADMIN)
    
    # Get current user's scope rule
    scope = "self"  # default
    if current_user.job_title_ref:
        scope = current_user.job_title_ref.data_scope
    
    # Apply scope-based filtering
    if scope == "all":
        # Full access but exclude ADMIN users (except for other ADMINS)
        return query.filter(User.role != UserRole.ADMIN)
    
    elif scope == "subtree":
        # Own org_unit + all descendants
        if current_user.org_unit_id is None:
            # Manager not assigned to a unit - no access to anyone
            return query.filter(False)
        
        descendant_ids = get_org_unit_descendants(current_user.org_unit_id)
        return query.filter(User.org_unit_id.in_(list(descendant_ids)))
    
    elif scope == "unit":
        # Only same org_unit
        if current_user.org_unit_id is None:
            return query.filter(False)
        return query.filter(User.org_unit_id == current_user.org_unit_id)
    
    else:  # scope == "self"
        # Only own record
        return query.filter(User.id == current_user.id)
