function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function updateElements(data) {
    // Seleccionamos los elementos por su clase
    var userElement = document.querySelector('.info-user');
    var bestElement = document.querySelector('.info-best');
    var worstElement = document.querySelector('.info-worst');
    var avgElement = document.querySelector('.info-avg');

    // Actualizamos el contenido de los elementos con los datos
    if (userElement) userElement.textContent = data.cantidad_usuarios;
    if (bestElement) bestElement.textContent = data.max_min_avg_scores[0];
    if (worstElement) worstElement.textContent = data.max_min_avg_scores[1];
    if (avgElement) avgElement.textContent = data.max_min_avg_scores[2].toFixed(2);
}

function inicializarDataTable(tableId, data) {
    $(`#${tableId}`).DataTable({
        responsive: true,
        data: data,
        columns: [
            {data: 'productId'},
            {data: 'userId'},
            {data: 'profileName'},
            {data: 'score'},
            {data: 'helpfulness'},
            {data: 'text'},
            {data: 'summary'},
            {data: 'time'},
        ],
        columnDefs: [
            {
                targets: [-1],
                render: function (data, type, row) {
                    if (data) {
                        var date = new Date(data);
                        var formattedDate = date.toISOString().split('T')[0];
                        return formattedDate;
                    }
                    return data;
                }
            }
        ],
        destroy: true
    });
}

function mostrarSpinner() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function ocultarSpinner() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

document.getElementById("searchForm").addEventListener("submit", function (event) {
    event.preventDefault();
    const fechaInicio = document.getElementById("fechaInicio").value;
    const fechaFin = document.getElementById("fechaFin").value;
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    if (fin <= inicio) {
        Swal.fire('Error', 'La fecha de fin debe ser mayor que la fecha de inicio.', 'error');
        return; // Detiene la ejecución de la función
    }
    const pelicula = document.getElementById("pelicula").value;
    const usuario = document.getElementById("usuario").value;
    const formData = new FormData();
    formData.append('fechaInicio', fechaInicio);
    formData.append('fechaFin', fechaFin);
    formData.append('pelicula', pelicula);
    formData.append('usuario', usuario);
    formData.append('csrfmiddlewaretoken', csrftoken);
    Swal.fire({
        title: 'Cargando...',
        html: 'Por favor espera mientras se procesan los datos.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading()
        },
    });
    fetch("/api/registros/", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            Swal.close();
            updateElements(data);
            inicializarDataTable('tablaPrimeros200', data.primeros_200);
            inicializarDataTable('tablaTop10Mejores', data.top_10_mejores);
            inicializarDataTable('tablaTop10Peores', data.top_10_peores);
            crearGrafico(data.visualizaciones);

        })
        .catch(error => {
            Swal.fire('Error', 'Ocurrió un error al enviar los datos: ' + error, 'error');
        });
});

function setupAutocomplete(inputId, url) {
    $(`#${inputId}`).autocomplete({
        source: function (request, response) {
            $.ajax({
                url: url,
                dataType: "json",
                data: {term: request.term},
                success: function (data) {
                    response(data);
                }
            });
        },
        open: function() {
            $(".ui-autocomplete").css({
                "background": "white",
                "opacity": "1"
            });
        },
        minLength: 2,
        delay: 200,
        select: function (event, ui) {
            // Acciones al seleccionar una sugerencia
        }
    });
}

setupAutocomplete("usuario", "/autocomplete/user/");
setupAutocomplete("pelicula", "/autocomplete/movie/");


function crearGrafico(datos) {
    var fechas = datos.map(function (d) {
        return d.fecha;
    });
    var promedioScore = datos.map(function (d) {
        return d.promedio_score;
    });
    var promedioHelpfulness = datos.map(function (d) {
        return d.promedio_helpfulness;
    });
    var trace1 = {
        x: fechas,
        y: promedioScore,
        name: 'Promedio de Score',
        type: 'scatter'
    };

    var trace2 = {
        x: fechas,
        y: promedioHelpfulness,
        name: 'Promedio de Helpfulness',
        yaxis: 'y2',
        type: 'scatter'
    };

    var layout = {
        title: 'Análisis de Reviews de Películas',
        yaxis: {title: 'Promedio de Score'},
        yaxis2: {
            title: 'Promedio de Helpfulness',
            overlaying: 'y',
            side: 'right'
        }
    };

    var data = [trace1, trace2];

    Plotly.newPlot('myPlot', data, layout);
}
