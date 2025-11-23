import frappe


def get_user_teams(user: str = frappe.session.user):
    """
    Get all Forms Pro teams for a user
    """

    FP_TEAM = frappe.qb.DocType("FP Team")
    FP_TEAM_MEMBER = frappe.qb.DocType("FP Team Member")

    query = (
        frappe.qb.from_(FP_TEAM)
        .join(FP_TEAM_MEMBER)
        .on(FP_TEAM.name == FP_TEAM_MEMBER.parent)
        .where(FP_TEAM_MEMBER.user == user)
        .select(FP_TEAM.team_name, FP_TEAM.name)
    )
    teams = query.run(as_dict=True)

    return teams or []
