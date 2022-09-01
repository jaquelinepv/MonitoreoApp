'use strict'
//urls servidor
//let urlCharM =  "http://127.0.0.1:8000/monitoreo/"
//let urlCharP =  "http://127.0.0.1:8000/predecir/"
let urlCharM ="https://iotacuicola.herokuapp.com/monitoreo/";
let urlCharP ="https://iotacuicola.herokuapp.com/predecir/";
//Etiquetas html
let resumenM = document.getElementById('datos_m');
let resumenP = document.getElementById('datos_p');
let chartM = "chartM";
let chartP = "chartP";

const ctx = document.getElementById(chartM).getContext('2d');
const ctp = document.getElementById(chartP).getContext('2d');

//Solicitar datos al servidor
var dataCm = $.get(urlCharM);
var dataP = $.get(urlCharP);

//Inicializar graficas
const myChartM = new Chart(ctx, {
    type: 'line',
    data: {
        labels: 0,
        datasets: [{
            label: 'Temperatura °C',
            data: 0,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            tension: 0.4,
            yAxisID: 'y'
        },{label: 'Oxígeno mg/L',
            data: 0,
            backgroundColor: 'rgba(0, 26, 104, 0.2)',
            borderColor: 'rgba(0, 26, 104, 1)',
            tension: 0.4,
            yAxisID: 'o'
        }]
    },
    options: {
        responsive:true,
        mantainApectRatio:false,
       
        layout:{
        padding:{
            bottom:0,
            right:20,
            left:20,
            top:0
        }
        
        },
        scales: {
            y: {
                beginAtZero: false,
                type: 'linear',
                position: 'left'
            },
            o:{
            beginAtZero: true,
                type: 'linear',
                position: 'right',
                grid:{
                drawOnChartArea: false

                }

            }
        }
    }
}); 


const myChartP = new Chart(ctp, {
    type: 'line',
    data: {
        labels: 0,
        datasets: [{
            label: 'Temperatura °C',
            data: 0,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            tension: 0.4,
            yAxisID: 'y'
        },{label: 'Oxígeno mg/L',
            data: 0,
            backgroundColor: 'rgba(0, 26, 104, 0.2)',
            borderColor: 'rgba(0, 26, 104, 1)',
            tension: 0.4,
            yAxisID: 'o'
        }]
    },
    options: {
        responsive:true,
        mantainApectRatio:false,
       
        layout:{
        padding:{
            bottom:0,
            right:20,
            left:20,
            top:0
        }
        
        },
        scales: {
            y: {
                beginAtZero: false,
                type: 'linear',
                position: 'left'
            },
            o:{
            beginAtZero: true,
                type: 'linear',
                position: 'right',
                grid:{
                drawOnChartArea: false

                }

            }
        }
    }
}); 

function mostrarResumen(Xf, Xhr, Yoxig, Ytemp, resumen ){
    //Sacar el utimo dato de cada arreglo para mostrarlo en el resumen
    var lastHr = Xhr[Xhr.length-1];
    var lastXf = Xf[Xf.length-1];
    var lastOxig = Yoxig[Yoxig.length-1];
    var lastTemp = Ytemp[Ytemp.length-1];
    //Muestrar el  resumen de la información en el cointainer 
    resumen.innerHTML = lastXf + ' - ' + lastHr + '<br>'  + 'Oxígeno disuelto: ' + lastOxig.toFixed(2) + ' mg/L' + '<br>' + 'Temperatura: ' + lastTemp.toFixed(2) + ' °C';
}

function updateChart(d1, d2, label, chart){

    chart.data.datasets[0].data=d1;
    chart.data.datasets[1].data=d2;
    chart.data.labels = label;
    console.log('se esta actualizando' + d1, d2, label);
    chart.update();
}

//Cargar por primera vez
dataCm.done(function(resp){
    //Almacenar los datos en arreglos separadons
    var Xhr=resp['hora']
    var Xf = resp['fecha']
    var Yoxig = resp['oxigeno']
    var Ytemp = resp['temperatura']

    mostrarResumen(Xf, Xhr, Yoxig, Ytemp, resumenM);
    updateChart(Ytemp, Yoxig, Xhr, myChartM);

});

dataP.done(function(resp){
    //Almacenar los datos en arreglos separadons
    var Xhr=resp['hora']
    var Xf = resp['fecha']
    var Yoxig = resp['oxigeno']
    var Ytemp = resp['temperatura']

    mostrarResumen(Xf, Xhr, Yoxig, Ytemp, resumenP);
    updateChart(Ytemp, Yoxig, Xhr, myChartP);
    

});

//Actualizar datos cada ciertos minutos
setInterval(()=>{
    var dataCm = $.get(urlCharM);
    dataCm.done(function(resp){
        //Almacanar los datos en arreglos separados
        var Xhr=resp['hora']
        var Xf = resp['fecha']
        var Yoxig = resp['oxigeno']
        var Ytemp = resp['temperatura']

        mostrarResumen(Xf, Xhr, Yoxig, Ytemp, resumenM);
        updateChart(Ytemp, Yoxig, Xhr, myChartM);
    

    });   
    
    var dataP = $.get(urlCharP);
    dataP.done(function(resp){
        //Almacanar los datos en arreglos separados
        var Xhr=resp['hora']
        var Xf = resp['fecha']
        var Yoxig = resp['oxigeno']
        var Ytemp = resp['temperatura']

        mostrarResumen(Xf, Xhr, Yoxig, Ytemp, resumenP);
        updateChart(Ytemp, Yoxig, Xhr, myChartP);

    });  
}, 60000);


    

