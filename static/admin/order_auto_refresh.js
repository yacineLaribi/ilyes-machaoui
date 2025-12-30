(function() {
    const SOUND_PATH = "/static/sounds/new_order.mp3";

    function playNotification() {
        const audio = new Audio(SOUND_PATH);
        audio.volume = 1;
        audio.play().catch(() => {});
    }

    // ---- AUDIO UNLOCK ----
    function unlockAudioOnce() {
        if (sessionStorage.getItem("audio_unlocked")) return;

        const audio = new Audio(SOUND_PATH);
        audio.muted = true;

        audio.play().then(() => {
            audio.pause();
            audio.muted = false;
            sessionStorage.setItem("audio_unlocked", "1");
            console.log("🔓 Audio unlocked");
        }).catch(() => {});
    }

    window.addEventListener("click", unlockAudioOnce, { once: true });
    window.addEventListener("keydown", unlockAudioOnce, { once: true });

    // ---- PLAY SOUND ON RELOAD (if triggered by new order) ----
    window.addEventListener("load", () => {
        if (sessionStorage.getItem("play_new_order_sound") === "1") {
            sessionStorage.removeItem("play_new_order_sound");
            playNotification();
            console.log("🔔 New order sound played after reload");
        }
    });

    // ---- POLLING WITH PERSISTENT LAST ID ----
    const INTERVAL = 15000;
    let lastKnownId = null;

    // Initialize lastKnownId from sessionStorage (survives reload)
    const storedId = sessionStorage.getItem("last_order_id");
    if (storedId) {
        lastKnownId = parseInt(storedId, 10);
        console.log("📦 Restored last known ID:", lastKnownId);
    }

    async function checkNewOrders() {
        try {
            const res = await fetch("/latest-order-meta/");
            const data = await res.json();

            console.log("Polling - Current ID:", data.last_id, "Last Known:", lastKnownId);

            // First time initialization
            if (lastKnownId === null) {
                lastKnownId = data.last_id;
                sessionStorage.setItem("last_order_id", lastKnownId);
                console.log("📝 Initialized last known ID:", lastKnownId);
                return;
            }

            // New order detected
            if (data.last_id > lastKnownId) {
                console.log("🆕 New order detected! Old ID:", lastKnownId, "New ID:", data.last_id);
                
                // Update stored ID BEFORE reload
                lastKnownId = data.last_id;
                sessionStorage.setItem("last_order_id", lastKnownId);
                
                // Set flag to play sound after reload
                sessionStorage.setItem("play_new_order_sound", "1");
                
                location.reload();
            }

        } catch (e) {
            console.warn("⚠️ Order polling failed", e);
        }
    }

    // Start polling immediately, then every INTERVAL
    checkNewOrders();
    setInterval(checkNewOrders, INTERVAL);

})();