document.getElementById('user-input').addEventListener("DOMContentLoaded", function () {
    // Send message when Enter key is pressed
    debugger;
    document.getElementById('user-input').addEventListener('keyup', function (e) {
        debugger;
        if (e.key === 'Enter') {
            e.preventDefault();
            document.getElementById("submit-question").click();
            return false;
        }
    });
});
