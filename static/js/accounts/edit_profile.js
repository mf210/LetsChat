document.getElementById('profile_image_input').addEventListener('change', (event) => {
    const imageFiles = event.target.files;
    const imageSrc = URL.createObjectURL(imageFiles[0]);
    document.getElementById('selected_profile_image').src = imageSrc
})