# Copyright (c) 2025, harsh@buildwithhussain.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_categories() -> list[dict]:
    """Get all categories with form counts"""
    categories = frappe.get_all(
        "Form Category",
        fields=["name", "title", "description", "color", "order"],
        order_by="COALESCE(`order`, 999999), title ASC"
    )
    
    # Get form counts for each category
    for category in categories:
        form_count = frappe.db.count("Form", {"category": category.name})
        category["form_count"] = form_count
    
    return categories


@frappe.whitelist()
def create_category(title: str, description: str = None, color: str = None, order: int = None) -> dict:
    """Create a new category"""
    category = frappe.get_doc({
        "doctype": "Form Category",
        "title": title,
        "description": description,
        "color": color,
        "order": order,
    })
    category.insert()
    return {
        "name": category.name,
        "title": category.title,
        "description": category.description,
        "color": category.color,
        "order": category.order,
    }


@frappe.whitelist()
def update_category(category_id: str, title: str = None, description: str = None, color: str = None, order: int = None) -> dict:
    """Update an existing category"""
    category = frappe.get_doc("Form Category", category_id)
    
    if title is not None:
        category.title = title
    if description is not None:
        category.description = description
    if color is not None:
        category.color = color
    if order is not None:
        category.order = order
    
    category.save()
    return {
        "name": category.name,
        "title": category.title,
        "description": category.description,
        "color": category.color,
        "order": category.order,
    }


@frappe.whitelist()
def delete_category(category_id: str) -> dict:
    """Delete a category"""
    # Check if any forms are using this category
    form_count = frappe.db.count("Form", {"category": category_id})
    if form_count > 0:
        frappe.throw(
            _("Cannot delete category. {0} form(s) are using this category.").format(form_count),
            frappe.ValidationError
        )
    
    category = frappe.get_doc("Form Category", category_id)
    category.delete()
    return {"success": True}


@frappe.whitelist()
def get_forms_by_category(category_id: str = None) -> list[dict]:
    """Get forms grouped by category, or forms for a specific category"""
    if category_id:
        # Get forms for a specific category
        forms = frappe.get_all(
            "Form",
            filters={"category": category_id, "owner": frappe.session.user},
            fields=["name", "title", "is_published", "route", "creation", "modified"],
            order_by="modified DESC"
        )
        return forms
    else:
        # Get all categories with their forms
        categories = get_categories()
        result = []
        
        for category in categories:
            forms = frappe.get_all(
                "Form",
                filters={"category": category.name, "owner": frappe.session.user},
                fields=["name", "title", "is_published", "route", "creation", "modified"],
                order_by="modified DESC"
            )
            result.append({
                **category,
                "forms": forms
            })
        
        # Also get uncategorized forms
        uncategorized_forms = frappe.get_all(
            "Form",
            filters={"category": ["in", ["", None]], "owner": frappe.session.user},
            fields=["name", "title", "is_published", "route", "creation", "modified"],
            order_by="modified DESC"
        )
        
        if uncategorized_forms:
            result.append({
                "name": None,
                "title": "Uncategorized",
                "description": None,
                "color": None,
                "order": 999999,
                "form_count": len(uncategorized_forms),
                "forms": uncategorized_forms
            })
        
        return result

