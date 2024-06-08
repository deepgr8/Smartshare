const dropzone = document.querySelector('.drop-zone');
const browseButton = document.querySelector('.browseButton');



dropzone.addEventListener('dragover',(e)=>{
    e.preventDefault()

    if (!dropzone.classList.contains('dragged')){
        dropzone.classList.add('dragged');
    }
    
});

dropzone.addEventListener('dragleave',()=>{
    dropzone.classList.remove('dragged');
});
dropzone.addEventListener('drop',(e)=>{
    e.preventDefault()
    dropzone.classList.remove('dragged');
});







