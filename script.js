function openModal() {
    document.getElementById('addProjectModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('addProjectModal').style.display = 'none';
    document.getElementById('addProjectForm').reset();
    toggleYearInput();
}

function toggleYearInput() {
    const select = document.getElementById('year_select');
    const customInput = document.getElementById('custom_year_div');
    if (select.value === 'other') {
        customInput.style.display = 'block';
        document.getElementById('year_custom').required = true;
    } else {
        customInput.style.display = 'none';
        document.getElementById('year_custom').required = false;
        document.getElementById('year_custom').value = '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const flash = document.querySelector('.flash-message');
    if (flash && flash.innerText.trim() !== "") {
        flash.classList.add('show');
        setTimeout(() => {
            flash.classList.remove('show');
        }, 2000);
    }
});

window.onclick = function(event) {
    const modal = document.getElementById('addProjectModal');
    if (event.target == modal) {
        closeModal();
    }
}