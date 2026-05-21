const money = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("es-CO");

async function getData(url) {
  const response = await fetch(url);
  return response.json();
}

function createChart(id, type, labels, data, label) {
  const ctx = document.getElementById(id);

  new Chart(ctx, {
    type,
    data: {
      labels,
      datasets: [
        {
          label,
          data,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
        },
      },
      scales: {
        y: {
          ticks: {
            callback: value => money.format(value),
          },
        },
      },
    },
  });
}

async function loadDashboard() {
  const kpis = await getData("/api/kpis");

  document.getElementById("totalVentas").textContent = number.format(kpis.total_ventas);
  document.getElementById("unidadesVendidas").textContent = number.format(kpis.unidades_vendidas);
  document.getElementById("ingresosTotales").textContent = money.format(kpis.ingresos_totales);
  document.getElementById("ticketPromedio").textContent = money.format(kpis.ticket_promedio);

  const ventasMes = await getData("/api/ventas-mes");
  createChart(
    "ventasMesChart",
    "line",
    ventasMes.map(item => item.nombre_mes),
    ventasMes.map(item => item.ingresos_totales),
    "Ingresos por mes"
  );

  const productos = await getData("/api/top-productos");
  createChart(
    "topProductosChart",
    "bar",
    productos.map(item => item.producto),
    productos.map(item => item.ingresos_totales),
    "Ingresos"
  );

  const categorias = await getData("/api/categorias");
  createChart(
    "categoriasChart",
    "bar",
    categorias.map(item => item.categoria),
    categorias.map(item => item.ingresos_totales),
    "Ingresos"
  );

  const subregiones = await getData("/api/subregiones");
  createChart(
    "subregionesChart",
    "bar",
    subregiones.map(item => item.subregion),
    subregiones.map(item => item.ingresos_totales),
    "Ingresos"
  );
}

async function loadProcess() {
  const status = await getData("/api/lakehouse-status");
  const calidad = await getData("/api/calidad-silver");
  const benchmark = await getData("/api/benchmark");
  const scd = await getData("/api/scd-producto");

  document.getElementById("bronzeRows").textContent =
    number.format(calidad.ventas_bronze) + " filas Bronze";

  document.getElementById("silverRows").textContent =
    number.format(calidad.ventas_silver) + " filas Silver";

  document.getElementById("goldRows").textContent =
    number.format(status.fact_ventas) + " filas Gold";

  document.getElementById("scdRows").textContent =
    number.format(status.dim_producto) + " registros DIM_PRODUCTO";

  createChart(
    "benchmarkChart",
    "bar",
    ["PostgreSQL", "DuckDB"],
    [benchmark.postgres_ms, benchmark.duckdb_ms],
    "Tiempo en ms"
  );

  createChart(
    "scdChart",
    "bar",
    scd.map(item => "Versión " + item.version_producto),
    scd.map(item => item.total_registros),
    "Registros por versión"
  );
}

loadDashboard();
loadProcess();