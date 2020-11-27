// Init
(function () {})();

function _now() {
    const date = $("#datepicker").val();
    const time = $("#timepicker").val();
    const ps = `${date}T${time}`.split(/\D/);
    return (
        new Date(ps[0], ps[1] - 1, ps[2], ps[3], ps[4], ps[5]).getTime() / 1000
    );
}

function updateProfile() {
    const now = _now();
    if (isNaN(now)) {
        return;
    }

    $("#profile")[0].src = `/profile/${now}`;
}

function imageError() {
    $("#profile")[0].src = "not-found.jpg";
}
