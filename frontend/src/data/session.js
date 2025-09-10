import router from "@/router";
import { createResource } from "frappe-ui";
import { computed, reactive } from "vue";

import { userResource } from "./user";

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	let _sessionUser = cookies.get("user_id");
	if (_sessionUser === "Guest") {
		_sessionUser = null;
	}
	return _sessionUser;
}

function fullName() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	let _fullName = cookies.get("full_name");
	return _fullName;
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			};
		},
		onSuccess(data) {
			userResource.reload();
			session.user = sessionUser();
			session.login.reset();
			router.replace(data.default_route || "/");
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset();
			session.user = sessionUser();
			window.location.href = `/login?redirect-to=/forms`;
		},
	}),
	user: sessionUser(),
	full_name: fullName(),
	isLoggedIn: computed(() => !!session.user),
});
