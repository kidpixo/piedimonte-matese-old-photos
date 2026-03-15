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

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

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

  // update visible counts element
  const photosCountEl = document.getElementById('photos-count');
  function updateCounts() {
    if (!photosCountEl || !table) return;
    try {
      const info = usesJqueryPlugin ? jQuery('#photos-table').DataTable().page.info() : table.page.info();
      photosCountEl.textContent = `${info.recordsDisplay} di ${info.recordsTotal} foto`;
    } catch (e) {
      // ignore
    }
  }

  // clear filters button
  const clearBtn = document.getElementById('clear-filters');
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      try {
        if (usesJqueryPlugin) {
          const dt = jQuery('#photos-table').DataTable();
          dt.search('').columns().search('');
          dt.order([]);
          dt.page('first').draw('page');
        } else {
          table.search('');
          if (table.columns) table.columns().search('');
          if (table.order) table.order([]);
          table.page('first').draw('page');
        }
      } catch (e) {
        console.error('Failed to clear filters', e);
      }
    });
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

    // hide only table body so DataTables controls (toolbar, pagination) remain visible
    const tbody = photosTableEl.querySelector('tbody');
    if (tbody) {
      if (isGrid) tbody.classList.add('d-none'); else tbody.classList.remove('d-none');
    }
    if (isGrid) photosGridEl.classList.remove('d-none'); else photosGridEl.classList.add('d-none');

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

      // title text from second column
      const titleNode = rowNode.querySelector('td:nth-child(2) a');
      const titleText = titleNode ? titleNode.textContent.trim() : (imageEl.alt || '');

      const photoLink = document.createElement('a');
      photoLink.href = imageLink.href;
      photoLink.className = 'photo-tile';
      photoLink.setAttribute('aria-label', titleText ? `Apri foto: ${titleText}` : 'Apri foto');
      if (titleText) photoLink.title = titleText;

      const gridImage = imageEl.cloneNode(true);
      gridImage.className = 'img-fluid';
      gridImage.style.width = '100%';
      gridImage.style.height = GRID_THUMB_HEIGHT;
      gridImage.style.objectFit = 'cover';
      gridImage.loading = gridImage.loading || 'lazy';

      photoLink.appendChild(gridImage);

      if (hasMap) {
        // gather year text (third column)
        const yearNode = rowNode.querySelector('td:nth-child(3)');
        const yearText = yearNode ? yearNode.textContent.trim() : '';

        // container for stacked badges (year + map)
        const badgesContainer = document.createElement('div');
        badgesContainer.className = 'badges-container position-absolute top-0 end-0 m-1 d-flex align-items-center';

        if (yearText) {
          const yearBadge = document.createElement('span');
          yearBadge.className = 'year-badge d-inline-flex align-items-center';
          yearBadge.setAttribute('aria-hidden', 'true');
          yearBadge.textContent = yearText;
          badgesContainer.appendChild(yearBadge);
        }

        const mapBadge = document.createElement('span');
        mapBadge.className = 'map-badge d-inline-flex align-items-center';
        mapBadge.setAttribute('aria-hidden', 'true');
        mapBadge.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="16" height="16" fill="currentColor" class="bi bi-map" viewBox="0 0 18 18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="m10.25 5.25v8.5m-4.5-10.5v8.5m-4 2.5v-9.5l4-2 4.5 2 4-2v9.5l-4 2-4.5-2z"></path></svg>';
        badgesContainer.appendChild(mapBadge);

        // append the badges container to the tile
        photoLink.appendChild(badgesContainer);
      }

      // always-visible caption under the image (no hover overlay)
      if (titleText) {
        const staticCaption = document.createElement('span');
        staticCaption.className = 'caption text-truncate';
        staticCaption.textContent = titleText;
        photoLink.appendChild(staticCaption);

        // for accessibility: announce if photo has a map
        if (hasMap) {
          const sr = document.createElement('span');
          sr.className = 'visually-hidden';
          sr.textContent = ' Foto con mappa';
          photoLink.appendChild(sr);
        }
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
    jQuery('#photos-table').on('draw.dt', function () { renderGridFromCurrentDataTableState(); updateCounts(); });
  } else {
    table.on('draw', function () { renderGridFromCurrentDataTableState(); updateCounts(); });
  }

  viewSwitchEl.addEventListener('change', function () {
    setViewMode(this.checked ? 'grid' : 'table');
  });
});
