import { onBeforeUnmount, onMounted, ref } from "vue";

export function useHashView(defaultView = "dashboard") {
  const readHash = () => {
    const value = window.location.hash.replace(/^#/, "");
    return value || defaultView;
  };

  const view = ref(defaultView);

  const syncView = () => {
    view.value = readHash();
  };

  const navigate = (nextView) => {
    if (nextView === view.value) {
      return;
    }

    window.location.hash = nextView;
    view.value = nextView;
  };

  onMounted(() => {
    syncView();
    window.addEventListener("hashchange", syncView);
  });

  onBeforeUnmount(() => {
    window.removeEventListener("hashchange", syncView);
  });

  return {
    view,
    navigate,
  };
}
