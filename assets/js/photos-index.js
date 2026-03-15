document.addEventListener('DOMContentLoaded', function () {
  const GRID_THUMB_HEIGHT = '140px';

  // Pre-filter from URL ?label=slug
  const params = new URLSearchParams(window.location.search);
  const prefilter = params.get('label') || '';
  const initialView = params.get('view') === 'grid' ? 'grid' : 'table';

  const viewSwitchEl = document.getElementById('view-switch');
  const photosGridEl = document.getElementById('photos-grid');
  const photosTableEl = document.getElementById('photos-table');

  if (!viewSwitchEl || !photosGridEl || !photosTableEl) {
    console.error('Photos index UI elements are missing. Check #view-switch, #photos-grid, #photos-table.');
    return;
  }

  const dtOptions = {
    order: [[2, 'desc']],        // default: sort by year descending
    ordering: true,
    searching: true,
    paging: true,
    info: true,
    lengthChange: true,
    pageLength: 25,
    lengthMenu: [10, 25, 50, 100],
    dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>rt<"row"<"col-sm-6"i><"col-sm-6"p>>',
    columnDefs: [
      { orderable: false, searchable: false, targets: [0] }
    ],
    language: {
      search:        'Cerca:',
      lengthMenu:    'Mostra _MENU_ foto',
      info:          'Da _START_ a _END_ di _TOTAL_ foto',
      infoEmpty:     'Nessuna foto trovata',
      infoFiltered:  '(filtrate da _MAX_ totali)',
      paginate: {
        first:    'Prima',
        last:     'Ultima',
        next:     'Avanti',
        previous: 'Indietro'
      },
      zeroRecords: 'Nessuna corrispondenza trovata'
    }
  };

  let table = null;
  let usesJqueryPlugin = false;
  if (typeof DataTable !== 'undefined') {
    table = new DataTable('#photos-table', dtOptions);
  } else if (window.jQuery && jQuery.fn && jQuery.fn.DataTable) {
    table = jQuery('#photos-table').DataTable(dtOptions);
    usesJqueryPlugin = true;
  } else {
    console.error('DataTables is not loaded. Check cdn_libs.jquery/datatables_js/datatables_bs5_js.');
    return;
  }

  function updateViewQueryParam(isGrid) {
    const nextParams = new URLSearchParams(window.location.search);
    if (isGrid) {
      nextParams.set('view', 'grid');
    } else {
      nextParams.delete('view');
    }

    const queryString = nextParams.toString();
    const nextUrl = `${window.location.pathname}${queryString ? `?${queryString}` : ''}`;
    window.history.replaceState({}, '', nextUrl);
  }

  function setViewMode(view) {
    const isGrid = view === 'grid';

    if (isGrid) {
      photosTableEl.classList.add('d-none');
      photosGridEl.classList.remove('d-none');
    } else {
      photosGridEl.classList.add('d-none');
      photosTableEl.classList.remove('d-none');
    }

    viewSwitchEl.checked = isGrid;
    updateViewQueryParam(isGrid);

    if (!isGrid && table.columns && typeof table.columns().adjust === 'function') {
      table.columns().adjust();
    }
  }

  function forEachCurrentRowNode(callback) {
    const rowsApi = table.rows({ page: 'current', search: 'applied', order: 'applied' });
    const nodes = rowsApi.nodes();

    if (!nodes) {
      return;
    }

    if (typeof nodes.each === 'function') {
      nodes.each(function (rowNode) {
        callback(rowNode);
      });
      return;
    }

    Array.from(nodes).forEach(function (rowNode) {
      callback(rowNode);
    });
  }

  function renderGridFromCurrentDataTableState() {
    const fragment = document.createDocumentFragment();
    let visibleItems = 0;

    forEachCurrentRowNode(function (rowNode) {
      const imageLink = rowNode.querySelector('td:nth-child(1) a') || rowNode.querySelector('td:nth-child(2) a');
      const imageEl = rowNode.querySelector('td:nth-child(1) img');
      const mapCell = rowNode.querySelector('td:nth-child(5)');
      const hasMap = mapCell && mapCell.textContent && mapCell.textContent.trim().length > 0;

      if (!imageLink || !imageEl) {
        return;
      }

      const gridColumn = document.createElement('div');
      gridColumn.className = 'col';

      const photoLink = document.createElement('a');
      photoLink.href = imageLink.href;
      photoLink.className = 'd-block position-relative';
      photoLink.setAttribute('aria-label', imageEl.alt || 'Apri foto');

      const gridImage = imageEl.cloneNode(true);
      gridImage.className = 'img-fluid rounded';
      gridImage.style.width = '100%';
      gridImage.style.height = GRID_THUMB_HEIGHT;
      gridImage.style.objectFit = 'cover';

      photoLink.appendChild(gridImage);

      if (hasMap) {
        const mapBadge = document.createElement('span');
        mapBadge.className = 'position-absolute top-0 end-0 m-1 p-1 rounded bg-dark text-white d-inline-flex';
        mapBadge.setAttribute('aria-label', 'Foto con mappa');
        mapBadge.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16" height="16" fill="currentColor" class="bi bi-map" viewBox="0 0 18 18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m10.25 5.25v8.5m-4.5-10.5v8.5m-4 2.5v-9.5l4-2 4.5 2 4-2v9.5l-4 2-4.5-2z"></path></svg>';
        photoLink.appendChild(mapBadge);
      }

      gridColumn.appendChild(photoLink);
      fragment.appendChild(gridColumn);
      visibleItems += 1;
    });

    photosGridEl.innerHTML = '';

    if (visibleItems === 0) {
      const emptyState = document.createElement('p');
      emptyState.className = 'text-muted mb-0';
      emptyState.textContent = 'Nessuna foto trovata';
      photosGridEl.appendChild(emptyState);
      return;
    }

    photosGridEl.appendChild(fragment);
  }

  // Apply URL pre-filter after init
  if (prefilter) {
    table.search(prefilter.replace(/-/g, ' ')).draw();
  }

  renderGridFromCurrentDataTableState();
  setViewMode(initialView);

  if (usesJqueryPlugin) {
    jQuery('#photos-table').on('draw.dt', renderGridFromCurrentDataTableState);
  } else {
    table.on('draw', renderGridFromCurrentDataTableState);
  }

  viewSwitchEl.addEventListener('change', function () {
    setViewMode(this.checked ? 'grid' : 'table');
  });
});
