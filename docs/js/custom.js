/** @param {HTMLIFrameElement} e */
function resizeIframe(e) {
    e.height = e.contentWindow.document.body.scrollHeight + 100;
}
window.addEventListener(
    "DOMContentLoaded",
    () => {
        const obs = new MutationObserver((arr_MutationList, observer) => {
            document.querySelectorAll("iframe").forEach((e) => {
                resizeIframe(e);
                e.contentWindow.addEventListener("DOMContentLoaded", () => resizeIframe(e), {
                    passive: true,
                });
            });
        });
        obs.observe(document.body, { childList: true, subtree: true });
    },
    { passive: true }
);
