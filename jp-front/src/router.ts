import { createRouter, createWebHistory } from "vue-router";
import AddVocab from "./views/AddVocab.vue";
import Quiz from "./views/Quiz.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: AddVocab },
    { path: "/quiz", component: Quiz },
  ],
});
