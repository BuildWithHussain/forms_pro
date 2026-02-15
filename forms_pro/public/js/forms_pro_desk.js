// Forms Pro: fix opening Form doctype documents from list view.
// The doctype name "Form" conflicts with the router's "form" view, so path-based
// navigation (/desk/form/docname) is misinterpreted. We patch set_route so that
// when called with a path like "/desk/form/<name>" we use ["Form", "Form", name].
(function () {
    if (typeof frappe === "undefined") return;

    const original_set_route = frappe.set_route;
    frappe.set_route = function () {
        const args = Array.from(arguments);
        if (args.length === 1 && typeof args[0] === "string" && args[0].includes("/")) {
            // Path string: e.g. "/desk/form/n8tqgeco1u" or "form/n8tqgeco1u"
            // Only match form/<docname> (one segment), not form/view/list etc.
            const m = args[0].match(/(?:^\/?(?:desk\/|app\/)?)?form\/([^/#?]+)(?=[#?]|$)/);
            if (m) {
                return original_set_route.apply(frappe.router, ["Form", "Form", m[1]]);
            }
        }
        return original_set_route.apply(frappe.router, args);
    };
})();
