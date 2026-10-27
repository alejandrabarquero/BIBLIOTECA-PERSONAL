const CLASES_ESTADO = {
    "No empezado": "estado-pendiente",
    "Empezado": "estado-leyendo",
    "En proceso": "estado-leyendo",
    "Terminado": "estado-leido"
};
const COLORES_PORTADA = ["#4a2523", "#34504a", "#26303a", "#7a5334", "#5a3a5e", "#3a4a2e"];

const FILTROS = {
    todos:     { titulo: "Añadidos recientemente", filtrar: () => true },
    leyendo:   { titulo: "Lo que estás leyendo",   filtrar: l => l.estado === "Empezado" || l.estado === "En proceso" },
    porleer:   { titulo: "Por leer",               filtrar: l => l.estado === "No empezado" },
    favoritos: { titulo: "Tus favoritos",          filtrar: l => l.favorito },
};

let libros = [];
let verTodos = false;
let editando = null;
let filtroActual = "todos";
let ordenActual = "recientes";

const ORDENES = {
    recientes: (a, b) => b.indice - a.indice,
    titulo:    (a, b) => (a.nombre || "").localeCompare(b.nombre || "", "es"),
    autor:     (a, b) => (a.autor || "").localeCompare(b.autor || "", "es"),
    progreso:  (a, b) => porcentaje(b) - porcentaje(a),
};

// ---------- Elementos (avisa en consola si falta alguno) ----------
const IDS = ["buscador", "lista-libros", "dialogo-libro", "form-libro", "error-form",
             "titulo-dialogo", "seccion-titulo", "banner-libro", "orden", "ver-todos",
             "btn-anadir", "btn-cancelar", "stat-total", "stat-total-detalle",
             "stat-terminados", "stat-terminados-detalle", "stat-espera"];

const faltan = IDS.filter(id => !document.getElementById(id));
if (faltan.length) console.error("Faltan estos id en el HTML:", faltan.join(", "));

const $ = (id) => document.getElementById(id);

// Pone un listener solo si el elemento existe
function on(id, evento, fn) {
    const el = $(id);
    if (el) el.addEventListener(evento, fn);
}

// Cambia el texto solo si el elemento existe
function texto(id, valor) {
    const el = $(id);
    if (el) el.textContent = valor;
}

function esc(valor) {
    const div = document.createElement("div");
    div.textContent = valor ?? "";
    return div.innerHTML;
}

// ---------- Datos ----------
async function cargarLibros() {
    try {
        const res = await fetch("/api/libros");
        if (!res.ok) throw new Error("Error " + res.status);
        libros = await res.json();
        render();
    } catch (err) {
        console.error("No se pudieron cargar los libros:", err);
        texto("banner-libro", "Error al cargar");
    }
}

function porcentaje(libro) {
    if (libro.estado === "Terminado") return 100;
    const total = parseInt(libro.paginas);
    if (!total) return 0;
    return Math.min(100, Math.round(((libro.leidas || 0) / total) * 100));
}

// ---------- Render ----------
function render() {
    renderBanner();
    renderEstadisticas();
    renderTarjetas();
}

function renderBanner() {
    const enCurso = libros.filter(l => l.estado === "Empezado" || l.estado === "En proceso");
    const libro = enCurso[enCurso.length - 1];

    if (libro) texto("banner-libro", libro.nombre);
    else if (libros.length) texto("banner-libro", "Elige tu próxima lectura");
    else texto("banner-libro", "Añade tu primer libro");
}

function renderEstadisticas() {
    const total = libros.length;
    const terminados = libros.filter(l => l.estado === "Terminado").length;
    const enEspera = libros.filter(l => l.estado === "No empezado").length;
    const mesActual = new Date().toISOString().slice(0, 7);
    const esteMes = libros.filter(l => (l.fecha || "").startsWith(mesActual)).length;
    const pct = total ? Math.round((terminados / total) * 100) : 0;

    texto("stat-total", total);
    texto("stat-total-detalle", `+${esteMes} este mes`);
    texto("stat-terminados", terminados);
    texto("stat-terminados-detalle", `${pct}% de tu colección`);
    texto("stat-espera", enEspera);
}

function renderTarjetas() {
    const contenedor = $("lista-libros");
    if (!contenedor) return;

    const buscado = ($("buscador")?.value || "").trim().toLowerCase();
    texto("seccion-titulo", FILTROS[filtroActual].titulo);

    let lista = libros.filter(FILTROS[filtroActual].filtrar);
    if (buscado) {
        lista = lista.filter(l =>
            (l.nombre || "").toLowerCase().includes(buscado) ||
            (l.autor || "").toLowerCase().includes(buscado)
        );
    } else if (filtroActual === "todos" && !verTodos) {
        lista = lista.slice(-4);
    }
    lista = [...lista].sort(ORDENES[ordenActual]);

    if (lista.length === 0) {
        const msg = buscado ? "No hay resultados para tu búsqueda."
                  : filtroActual === "todos" ? "Aún no tienes libros. ¡Añade el primero!"
                  : "No hay libros en esta categoría.";
        contenedor.innerHTML = `<p class="vacio">${msg}</p>`;
        return;
    }

    contenedor.innerHTML = lista.map(libro => {
        const enCurso = libro.estado === "Empezado" || libro.estado === "En proceso";
        const pct = porcentaje(libro);
        const progreso = enCurso && parseInt(libro.paginas) ? `
            <div class="progreso">
                <div class="progreso-barra"><div class="progreso-relleno" style="width: ${pct}%"></div></div>
                <span class="progreso-porcentaje">${pct}%</span>
            </div>` : "";

        return `
        <article class="tarjeta-libro">
            <div class="portada" style="background-color: ${COLORES_PORTADA[libro.indice % COLORES_PORTADA.length]}">
                <span class="portada-adorno">✦</span>
                <strong class="portada-titulo">${esc(libro.nombre)}</strong>
                <span class="portada-autor">${esc(libro.autor)}</span>
            </div>
            <div class="tarjeta-info">
                <span class="estado ${CLASES_ESTADO[libro.estado] || ""}">${esc(libro.estado)}</span>
                <h3 class="tarjeta-titulo">${esc(libro.nombre)}</h3>
                <p class="tarjeta-detalle">${esc(libro.autor)}${libro.paginas ? " · " + esc(libro.paginas) + " págs." : ""}</p>
                ${progreso}
                <div class="tarjeta-acciones">
                    <button class="btn-fav ${libro.favorito ? "activo" : ""}" data-indice="${libro.indice}" title="Favorito">${libro.favorito ? "★" : "☆"}</button>
                    <button class="btn-editar" data-indice="${libro.indice}">Editar</button>
                    <button class="btn-borrar" data-indice="${libro.indice}">Borrar</button>
                </div>
            </div>
        </article>`;
    }).join("");
}

// ---------- Diálogo: añadir / editar ----------
function abrirDialogo(libro = null) {
    const form = $("form-libro");
    form.reset();
    texto("error-form", "");

    if (libro) {
        editando = libro.indice;
        texto("titulo-dialogo", "Editar libro");
        form.elements.nombre.value = libro.nombre ?? "";
        form.elements.autor.value = libro.autor ?? "";
        form.elements.paginas.value = libro.paginas ?? "";
        if (form.elements.leidas) form.elements.leidas.value = libro.leidas ?? 0;
        form.elements.estado.value = libro.estado;
    } else {
        editando = null;
        texto("titulo-dialogo", "Añadir libro");
    }
    $("dialogo-libro").showModal();
}

// ---------- Eventos ----------
document.querySelectorAll(".menu a[data-filtro]").forEach(enlace => {
    enlace.addEventListener("click", (e) => {
        e.preventDefault();
        filtroActual = enlace.dataset.filtro;
        document.querySelectorAll(".menu li").forEach(li => li.classList.remove("activo"));
        enlace.parentElement.classList.add("activo");
        renderTarjetas();
    });
});

on("buscador", "input", renderTarjetas);

on("orden", "change", (e) => {
    ordenActual = e.target.value;
    renderTarjetas();
});

on("ver-todos", "click", (e) => {
    e.preventDefault();
    verTodos = !verTodos;
    e.target.textContent = verTodos ? "Ver menos" : "Ver todos";
    renderTarjetas();
});

on("lista-libros", "click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const indice = Number(btn.dataset.indice);
    const libro = libros.find(l => l.indice === indice);
    if (!libro) return;

    if (btn.classList.contains("btn-fav")) {
        await fetch(`/api/libros/${indice}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ favorito: !libro.favorito }),
        });
        await cargarLibros();
    }

    if (btn.classList.contains("btn-borrar")) {
        if (!confirm(`¿Borrar "${libro.nombre}"?`)) return;
        const res = await fetch(`/api/libros/${indice}`, { method: "DELETE" });
        if (!res.ok) { alert("No se pudo borrar el libro."); return; }
        await cargarLibros();
    }

    if (btn.classList.contains("btn-editar")) {
        abrirDialogo(libro);
    }
});

on("btn-anadir", "click", () => abrirDialogo());
on("btn-cancelar", "click", () => $("dialogo-libro").close());

on("form-libro", "submit", async (e) => {
    e.preventDefault();
    const datos = Object.fromEntries(new FormData($("form-libro")));

    const esEdicion = editando !== null;
    const res = await fetch(esEdicion ? `/api/libros/${editando}` : "/api/libros", {
        method: esEdicion ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
    });

    if (!res.ok) {
        const err = await res.json();
        texto("error-form", err.error);
        return;
    }

    await cargarLibros();
    $("dialogo-libro").close();
});

cargarLibros();