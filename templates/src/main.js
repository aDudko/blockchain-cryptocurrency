import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import Node from "./components/Node.vue";
import Network from "./components/Network.vue";
import "./style.css";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: Node },
        { path: "/network", component: Network },
    ],
});

createApp(App).use(router).mount("#app");