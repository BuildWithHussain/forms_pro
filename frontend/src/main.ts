import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";
import { initSocket } from "./socket";

import {
  Alert,
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FormControl,
  Input,
  TextInput,
  frappeRequest,
  pageMetaPlugin,
  resourcesPlugin,
  setConfig,
} from "frappe-ui";

import "./index.css";

const globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
};

const app = createApp(App);
const pinia = createPinia();

setConfig("resourceFetcher", frappeRequest);

app.use(pinia);
app.use(router);
app.use(resourcesPlugin);
app.use(pageMetaPlugin);

const socket = initSocket();
app.config.globalProperties.$socket = socket;

for (const key in globalComponents) {
  app.component(key, globalComponents[key]);
}

app.mount("#app");
