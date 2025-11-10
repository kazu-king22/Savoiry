document.addEventListener('DOMContentLoaded', function() {
  const addButton = document.getElementById('add-tag');
  const container = document.getElementById('tag-container');

  addButton.addEventListener('click', function() {
    const newInput = document.createElement('p');
    newInput.innerHTML = '<input type="text" name="tags" class="tag-input">';
    container.appendChild(newInput);
  });
});
