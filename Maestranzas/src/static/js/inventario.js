const productTable = document.getElementById("product-table").querySelector("tbody");
const searchInput = document.querySelector('input[type="search"]');



document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
});

function loadProducts() {
  const products = getProductsFromLocalStorage();
  productTable.innerHTML = ""; // Limpia la tabla antes de cargar
  products.forEach((product) => addProductToTable(product));
}

// AGREGAR PRODUCTO A TABLA

// Contenido de tu_archivo_js.js
document.addEventListener('DOMContentLoaded', function () {
  // La variable is_editor es definida en la plantilla Flask
  if (is_editor) {
    console.log("Eres un editor");
    // Haz lo que necesites hacer si es un editor
  } else {
    console.log("No eres un editor");
    // Haz lo que necesites hacer si no es un editor
  }
});

function addProductToTable(product) {
  const row = document.createElement("tr");

  row.innerHTML = `
    <td data-field="id">${product.id}</td>
    <td data-field="name">${product.name}</td>
    <td data-field="desc">${product.desc}</td>
    <td data-field="ubi">${product.ubi}</td>
    <td data-field="cant">${product.cant}</td>
    <td data-field="pdf">${product.pdf}</td>
    <td data-field="categ">${product.categ}</td>
    

    <td>
      <button class="btn btn-danger btn-sm delete-product">
        <i class="bi bi-trash3-fill"></i>
      </button>
      <button class="btn btn-primary btn-sm edit-product" data-product-id="${product.id}">
        <i class="bi bi-pen-fill"></i>
      </button>
    </td>

    

  `;

  productTable.appendChild(row);

  // Configurar el evento para eliminar
  row.querySelector(".delete-product").addEventListener("click", () => {
    productTable.removeChild(row);
    const products = getProductsFromLocalStorage();
    const updatedProducts = products.filter((p) => p.id !== product.id);
    setProductsInLocalStorage(updatedProducts);
  });

  // Configurar el evento para editar
  row.querySelector(".edit-product").addEventListener("click", (e) => {
    const productId = e.currentTarget.getAttribute("data-product-id");
    window.location.href = `editProduct.html?id=${productId}`; // Agregar el ID como parámetro en la URL
  });
}

// Función para obtener productos del almacenamiento local
function getProductsFromLocalStorage() {
  const productsJSON = localStorage.getItem("products");
  return productsJSON ? JSON.parse(productsJSON) : [];
}

// Función para guardar productos en el almacenamiento local
function setProductsInLocalStorage(products) {
  localStorage.setItem("products", JSON.stringify(products));
}

document.addEventListener("DOMContentLoaded", function () {
  const table = document.getElementById('product-table');
  const tbody = table.querySelector('tbody');
  const dropdownItems = document.querySelectorAll('.dropdown-item');

  dropdownItems.forEach(item => {
    item.addEventListener('click', function () {
      const field = this.textContent.trim().toLowerCase();
      const rows = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${getIndex(field)})`).textContent.trim();
        const bValue = b.querySelector(`td:nth-child(${getIndex(field)})`).textContent.trim();
        return compareValues(aValue, bValue);
      });

      while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
      }

      rows.forEach(row => {
        tbody.appendChild(row);
      });
    });
  });

  function getIndex(field) {
    switch (field) {
      case 'número de serie':
        return 1;
      case 'nombre':
        return 2;
      case 'descripción':
        return 3;
      case 'ubicación':
        return 4;
      case 'cantidad':
        return 5;
      case 'ficha técnica':
        return 6;
      case 'categoría':
        return 7;
      default:
        return 0;
    }
  }

  function compareValues(a, b) {
    if (isNaN(a) || isNaN(b)) {
      return a.localeCompare(b, undefined, { sensitivity: 'base' });
    } else {
      return parseInt(a) - parseInt(b);
    }
  }
});


document.addEventListener("DOMContentLoaded", function () {
  const searchBar = document.querySelector('input[type="search"]');
  const productRows = document.querySelectorAll("#product-table tbody tr");

  searchBar.addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase();

    productRows.forEach(function (row) {
      let found = false;

      row.querySelectorAll("td").forEach(function (cell) {
        const cellText = cell.textContent.toLowerCase();
        if (cellText.includes(searchTerm)) {
          found = true;
        }
      });

      if (found) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });
}); 