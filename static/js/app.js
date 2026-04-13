function calculateFare() {
    const level = document.getElementById("tripLevel");
    const truck = document.getElementById("truckType");
    const weight = document.getElementById("loadWeight");
    const estimate = document.getElementById("estimateAmount");

    if (!level || !truck || !weight || !estimate) return;

    const tripLevel = level.value;
    const truckType = truck.value;
    const loadWeight = parseFloat(weight.value || "0");

    let price = 0;

    if (tripLevel === "District Level") {
        price = 2200;
    } else if (tripLevel === "State Level") {
        price = 3800;
    } else if (tripLevel === "Indian Level") {
        price = 5600;
    }

    if (truckType === "Pickup") price += 1000;
    else if (truckType === "Mini Truck") price += 1500;
    else if (truckType === "Light Commercial") price += 2200;
    else if (truckType === "Heavy Truck") price += 4200;
    else if (truckType === "Trailer" || truckType === "Trailer Truck") price += 7000;
    else if (truckType === "Container Truck") price += 6500;

    if (loadWeight > 0) price += Math.round(loadWeight * 1000);

    if (!tripLevel || !truckType || loadWeight <= 0) {
        estimate.innerText = "₹ 0";
        return;
    }

    estimate.innerText = "₹ " + price.toLocaleString("en-IN");
}

function selectTruck(truckName) {
    const truckDropdown = document.getElementById("truckType");
    const bookingSection = document.getElementById("booking");
    if (truckDropdown) truckDropdown.value = truckName;
    if (bookingSection) bookingSection.scrollIntoView({ behavior: "smooth" });
}

async function captureDriverLocation() {
    const gpsStatus = document.getElementById("gpsStatus");
    const currentLocationInput = document.getElementById("currentLocationInput");
    const driverLocationText = document.getElementById("driverLocationText");

    if (!navigator.geolocation) {
        if (gpsStatus) gpsStatus.textContent = "GPS not supported in this browser";
        return;
    }

    if (gpsStatus) gpsStatus.textContent = "Getting current location...";

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const latitude = position.coords.latitude.toFixed(6);
            const longitude = position.coords.longitude.toFixed(6);
            const place = `GPS ${latitude}, ${longitude}`;

            try {
                const response = await fetch("/driver/location-update", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        latitude,
                        longitude,
                        place,
                    }),
                });

                const data = await response.json();

                if (data.success) {
                    if (currentLocationInput) currentLocationInput.value = data.location;
                    if (driverLocationText) driverLocationText.textContent = data.location;
                    if (gpsStatus) gpsStatus.textContent = "Location updated successfully";
                } else {
                    if (gpsStatus) gpsStatus.textContent = data.message || "Location update failed";
                }
            } catch (error) {
                if (gpsStatus) gpsStatus.textContent = "Server connection failed";
            }
        },
        () => {
            if (gpsStatus) gpsStatus.textContent = "Location permission denied";
        }
    );
}

async function requestBrowserNotificationPermission() {
    if (!("Notification" in window)) return;
    if (Notification.permission === "default") {
        await Notification.requestPermission();
    }
}

function showBrowserNotification(title, body) {
    if (!("Notification" in window)) return;
    if (Notification.permission === "granted") {
        new Notification(title, { body });
    }
}

let lastAlertCount = null;

async function pollOwnerAlerts() {
    const alertList = document.getElementById("alertList");
    if (!alertList) return;

    try {
        const response = await fetch("/api/alerts");
        const alerts = await response.json();

        const openAlerts = alerts.filter((item) => item.status === "Open");

        if (lastAlertCount !== null && openAlerts.length > lastAlertCount && openAlerts.length > 0) {
            const latest = openAlerts[0];
            showBrowserNotification("Eagle Transport Alert", `${latest.alert_type}: ${latest.message}`);
        }
        lastAlertCount = openAlerts.length;
    } catch (error) {
        console.log("Alert polling failed");
    }
}

async function pollDashboardSummary() {
    const liveBookingCount = document.getElementById("liveBookingCount");
    const pendingTollCount = document.getElementById("pendingTollCount");
    const totalTollAmount = document.getElementById("totalTollAmount");

    if (!liveBookingCount && !pendingTollCount && !totalTollAmount) return;

    try {
        const response = await fetch("/api/dashboard-summary");
        const data = await response.json();

        if (liveBookingCount) liveBookingCount.textContent = data.active_bookings;
        if (pendingTollCount) pendingTollCount.textContent = data.pending_tolls;
        if (totalTollAmount) totalTollAmount.textContent = "₹" + Number(data.total_toll_amount).toLocaleString("en-IN");
    } catch (error) {
        console.log("Summary polling failed");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const bookingForm = document.getElementById("bookingForm");
    const tripLevel = document.getElementById("tripLevel");
    const truckType = document.getElementById("truckType");
    const loadWeight = document.getElementById("loadWeight");

    if (tripLevel) tripLevel.addEventListener("change", calculateFare);
    if (truckType) truckType.addEventListener("change", calculateFare);
    if (loadWeight) loadWeight.addEventListener("input", calculateFare);

    if (bookingForm) {
        bookingForm.addEventListener("submit", function (event) {
            const customerName = bookingForm.querySelector('input[name="customer_name"]');
            const mobile = bookingForm.querySelector('input[name="mobile"]');
            const pickup = bookingForm.querySelector('input[name="pickup_location"]');
            const drop = bookingForm.querySelector('input[name="drop_location"]');
            const goods = bookingForm.querySelector('input[name="goods_type"]');

            if (
                !customerName.value.trim() ||
                !mobile.value.trim() ||
                !pickup.value.trim() ||
                !drop.value.trim() ||
                !tripLevel.value.trim() ||
                !truckType.value.trim() ||
                !goods.value.trim() ||
                !loadWeight.value.trim()
            ) {
                event.preventDefault();
                alert("Please fill all booking details.");
                return;
            }

            if (mobile.value.trim().length < 10) {
                event.preventDefault();
                alert("Please enter a valid mobile number.");
            }
        });
    }

    requestBrowserNotificationPermission();
    pollOwnerAlerts();
    pollDashboardSummary();
    setInterval(pollOwnerAlerts, 15000);
    setInterval(pollDashboardSummary, 15000);
});

const heroImages = [
    "/static/images/bg1.jpg",
    "/static/images/bg2.jpg",
    "/static/images/bg3.jpg",
    "/static/images/bg4.jpg",
    "/static/images/bg5.jpg"
];

let heroIndex = 0;

function startHeroBackgroundSlider() {
    const heroBgSlider = document.getElementById("heroBgSlider");
    if (!heroBgSlider) return;

    setInterval(() => {
        heroIndex = (heroIndex + 1) % heroImages.length;
        heroBgSlider.style.backgroundImage = `url('${heroImages[heroIndex]}')`;
    }, 50000);
}

document.addEventListener("DOMContentLoaded", function () {
    startHeroBackgroundSlider();
});

function startHeroBackgroundSlider() {
    const heroBgSlider = document.getElementById("heroBgSlider");
    if (!heroBgSlider) return;

    const heroImages = [
        "/static/images/bg1.jpg",
        "/static/images/bg2.jpg",
        "/static/images/bg3.jpg",
        "/static/images/bg4.jpg",
        "/static/images/bg5.jpg"
    ];

    let heroIndex = 0;
    heroBgSlider.style.backgroundImage = `url('${heroImages[0]}')`;

    setInterval(() => {
        heroIndex = (heroIndex + 1) % heroImages.length;
        heroBgSlider.style.backgroundImage = `url('${heroImages[heroIndex]}')`;
    }, 3000);
}

function initMobileMenu() {
    const menuToggle = document.getElementById("menuToggle");
    const mobileNav = document.getElementById("mobileNav");

    if (!menuToggle || !mobileNav) return;

    menuToggle.addEventListener("click", function () {
        mobileNav.classList.toggle("show");
    });

    mobileNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", function () {
            mobileNav.classList.remove("show");
        });
    });
    initMobileMenu();
    startHeroBackgroundSlider();
}
