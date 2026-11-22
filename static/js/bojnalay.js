/* ==========================================================================
   BOJNALAY — Planner engine, live macro calculator & grocery checklist
   ========================================================================== */

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const SLOTS = ["breakfast", "lunch", "snack", "dinner"];
const CATEGORIES = ["All", "Breakfast", "Main Course", "Snack", "Dessert", "Healthy Bowl"];
const RING_CIRCUMFERENCE = 2 * Math.PI * 52;

const state = {
  recipes: [],
  plan: {},
  selectedDay: DAYS[0],
  category: "All",
  search: "",
  modalRecipeId: null,
  assignContext: { day: DAYS[0], slot: "lunch" },
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

function asset(name) {
  return `/static/assets/${String(name || "food-bowl.jpg").replace(/[^a-zA-Z0-9._-]/g, "")}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let data;
  try { data = await response.json(); } catch { data = { error: "Invalid server response" }; }
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function toast(message, type = "success") {
  const node = document.createElement("div");
  node.className = `toast ${type}`;
  node.textContent = message;
  $("#toastStack").appendChild(node);
  setTimeout(() => {
    node.style.opacity = "0";
    node.style.transform = "translateX(30px)";
    node.style.transition = "all .3s ease";
    setTimeout(() => node.remove(), 320);
  }, 3200);
}

/* ------------------------------- Day picker ----------------------------- */
function renderDayPicker() {
  $("#dayPicker").innerHTML = DAYS.map((day) => `
    <button type="button" role="tab" aria-selected="${day === state.selectedDay}"
      class="${day === state.selectedDay ? "active" : ""}" data-day="${day}">${day.slice(0, 3)}</button>
  `).join("");
  $$("#dayPicker button").forEach((button) => button.addEventListener("click", () => {
    state.selectedDay = button.dataset.day;
    renderDayPicker();
    refreshNutrition();
    document.querySelectorAll(".day-column").forEach((col) =>
      col.classList.toggle("today", col.dataset.day === state.selectedDay));
  }));
}

/* -------------------------------- Planner ------------------------------- */
function renderPlanner() {
  const todayName = new Date().toLocaleDateString("en-US", { weekday: "long" });
  $("#plannerGrid").innerHTML = DAYS.map((day) => {
    let dayKcal = 0;
    const slots = SLOTS.map((slot) => {
      const meal = state.plan[`${day}|${slot}`];
      if (meal) dayKcal += Number(meal.calories || 0);
      if (meal) {
        return `
          <div class="meal-slot filled" data-slot="${slot}">
            <div class="slot-top"><span class="slot-label">${slot}</span><span class="slot-kcal">${Math.round(meal.calories)} kcal</span></div>
            <img class="slot-thumb" src="${asset(meal.image)}" alt="" loading="lazy">
            <p class="slot-meal-name">${escapeHtml(meal.name)}</p>
            <span class="slot-macros">P ${Math.round(meal.protein)}g · C ${Math.round(meal.carbs)}g · F ${Math.round(meal.fats)}g</span>
            <button class="slot-change" data-day="${day}" data-slot="${slot}" data-recipe="${meal.recipe_id}">Change</button>
          </div>`;
      }
      return `
        <div class="meal-slot" data-slot="${slot}">
          <div class="slot-top"><span class="slot-label">${slot}</span></div>
          <button class="slot-add" data-day="${day}" data-slot="${slot}">＋ Assign recipe</button>
        </div>`;
    }).join("");
    return `
      <article class="day-column glass ${day === todayName || day === state.selectedDay ? "today" : ""}" data-day="${day}">
        <div class="day-header">
          <h3>${day.slice(0, 3)}</h3>
          <span class="day-kcal ${dayKcal > 2200 ? "over" : ""}">${dayKcal} kcal</span>
        </div>
        ${slots}
      </article>`;
  }).join("");

  $$("#plannerGrid .slot-add").forEach((button) => button.addEventListener("click", () =>
    openAssign(button.dataset.day, button.dataset.slot)));
  $$("#plannerGrid .slot-change").forEach((button) => button.addEventListener("click", (event) => {
    event.stopPropagation();
    openAssign(button.dataset.day, button.dataset.slot, Number(button.dataset.recipe));
  }));
}

/* --------------------------- Nutrition & rings -------------------------- */
function renderRings(rings) {
  Object.keys(rings).forEach((key) => {
    const data = rings[key];
    const circle = $(`.ring-card[data-ring="${key}"] .ring-progress`);
    const offset = RING_CIRCUMFERENCE * (1 - Math.min(data.percent, 100) / 100);
    circle.style.strokeDashoffset = String(offset);
    $(`#val-${key}`).textContent = data.value.toLocaleString("en-IN");
    $(`#pct-${key}`).textContent = `${data.percent}%`;
  });

  $("#liveDay").textContent = state.selectedDay.toUpperCase();
  $("#liveKcal").textContent = rings.calories.value.toLocaleString("en-IN");
  $("#liveProtein").textContent = `${rings.protein.value}g`;
  $("#liveCarbs").textContent = `${rings.carbs.value}g`;
  $("#liveFats").textContent = `${rings.fats.value}g`;
  $("#liveBar").style.width = `${Math.min(rings.calories.percent, 100)}%`;
}

async function refreshNutrition() {
  const data = await api(`/api/nutrition?day=${encodeURIComponent(state.selectedDay)}`);
  renderRings(data.rings);
}

function renderWeekTotals(data) {
  $("#weekMeals").textContent = Object.keys(data.plan).length;
  $("#weekKcal").textContent = data.week.calories.toLocaleString("en-IN");
  $("#weekProtein").textContent = data.week.protein.toLocaleString("en-IN");
}

/* ------------------------------ Recipe vault ---------------------------- */
function renderFilters() {
  $("#categoryFilters").innerHTML = CATEGORIES.map((category) => `
    <button type="button" class="${category === state.category ? "active" : ""}" data-category="${category}">${category}</button>
  `).join("");
  $$("#categoryFilters button").forEach((button) => button.addEventListener("click", () => {
    state.category = button.dataset.category;
    renderFilters();
    renderRecipes();
  }));
}

function renderRecipes() {
  const query = state.search.toLowerCase().trim();
  const filtered = state.recipes.filter((recipe) => {
    const matchesCategory = state.category === "All" || recipe.category === state.category;
    const haystack = `${recipe.name} ${recipe.cuisine} ${recipe.description} ${recipe.tags}`.toLowerCase();
    return matchesCategory && (!query || haystack.includes(query));
  });

  $("#resultCount").textContent = `${filtered.length} recipe${filtered.length === 1 ? "" : "s"}`;
  $("#recipeEmpty").hidden = filtered.length > 0;
  $("#recipeGrid").innerHTML = filtered.map((recipe, index) => `
    <article class="recipe-card glass" style="animation-delay:${Math.min(index * 45, 400)}ms">
      <div class="recipe-photo-wrap">
        <img class="recipe-photo" src="${asset(recipe.image)}" alt="${escapeHtml(recipe.name)}" loading="lazy">
        <span class="recipe-cuisine">${escapeHtml(recipe.cuisine)}</span>
        <span class="recipe-time">◷ ${recipe.prep_time} min</span>
        <span class="recipe-kcal-overlay">${Math.round(recipe.calories)}<small>kcal</small></span>
      </div>
      <div class="recipe-card-body">
        <h3>${escapeHtml(recipe.name)}${recipe.is_custom ? '<span class="custom-badge">CUSTOM</span>' : ""}</h3>
        <div class="macro-badges">
          <div><b class="p">${Math.round(recipe.protein)}g</b><small>protein</small></div>
          <div><b class="c">${Math.round(recipe.carbs)}g</b><small>carbs</small></div>
          <div><b class="f">${Math.round(recipe.fats)}g</b><small>fats</small></div>
        </div>
        <div class="recipe-card-actions">
          <button class="btn btn-outline" data-view="${recipe.id}">View Recipe</button>
          <button class="btn-mini" data-quick="${recipe.id}">＋ Plan</button>
        </div>
      </div>
    </article>
  `).join("");

  $$("[data-view]").forEach((button) => button.addEventListener("click", () =>
    openRecipeModal(Number(button.dataset.view))));
  $$("[data-quick]").forEach((button) => button.addEventListener("click", () => {
    const recipe = state.recipes.find((r) => r.id === Number(button.dataset.quick));
    openAssign(state.selectedDay, "lunch", recipe.id);
    $("#assignRecipe").value = String(recipe.id);
    toast(`Pick a slot for ${recipe.name}`);
  }));
}

function openRecipeModal(id) {
  const recipe = state.recipes.find((r) => r.id === id);
  if (!recipe) return;
  state.modalRecipeId = id;
  $("#modalRecipeImage").style.backgroundImage = `linear-gradient(0deg, rgba(28,25,23,0.5), transparent), url('${asset(recipe.image)}')`;
  $("#modalRecipeTags").innerHTML = recipe.tags.split(",").filter(Boolean)
    .map((tag) => `<span>${escapeHtml(tag.trim())}</span>`).join("");
  $("#recipeModalTitle").textContent = recipe.name;
  $("#modalRecipeDesc").textContent = recipe.description;
  $("#modalRecipeMacros").innerHTML = `
    <div><b style="color:var(--saffron)">${Math.round(recipe.calories)}</b><small>kcal</small></div>
    <div><b style="color:var(--mint)">${Math.round(recipe.protein)}g</b><small>protein</small></div>
    <div><b style="color:var(--turmeric)">${Math.round(recipe.carbs)}g</b><small>carbs</small></div>
    <div><b style="color:#FDBA74">${Math.round(recipe.fats)}g</b><small>fats</small></div>`;
  $("#modalRecipeIngredients").innerHTML = recipe.ingredients.map((ing) => {
    const item = typeof ing === "string" ? ing : ing.item;
    const qty = typeof ing === "string" ? "" : ing.qty;
    return `<li><b>${escapeHtml(item)}</b>${qty ? ` — ${escapeHtml(qty)}` : ""}</li>`;
  }).join("");
  $("#modalRecipeSteps").innerHTML = recipe.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  $("#recipeModal").hidden = false;
}

/* ------------------------------ Assign modal ---------------------------- */
function openAssign(day, slot, recipeId = null) {
  state.assignContext = { day, slot };
  state.modalRecipeId = recipeId;
  $("#assignModalSub").textContent = `Choose where ${recipeId ? "this recipe" : "your next delicious meal"} belongs in the weekly thali.`;
  $("#assignDay").innerHTML = DAYS.map((d) => `<option value="${d}" ${d === day ? "selected" : ""}>${d}</option>`).join("");
  $("#assignSlot").innerHTML = SLOTS.map((s) => `<option value="${s}" ${s === slot ? "selected" : ""}>${s[0].toUpperCase() + s.slice(1)}</option>`).join("");
  $("#assignRecipe").innerHTML = state.recipes.map((r) =>
    `<option value="${r.id}" ${r.id === recipeId ? "selected" : ""}>${escapeHtml(r.name)} · ${Math.round(r.calories)} kcal</option>`).join("");
  $("#recipeModal").hidden = true;
  $("#assignModal").hidden = false;
}

async function confirmAssign() {
  const payload = {
    day: $("#assignDay").value,
    slot: $("#assignSlot").value,
    recipe_id: Number($("#assignRecipe").value),
  };
  try {
    const result = await api("/api/plan", { method: "POST", body: JSON.stringify(payload) });
    state.plan = result.plan;
    state.selectedDay = payload.day;
    $("#assignModal").hidden = true;
    renderDayPicker();
    renderPlanner();
    await refreshNutrition();
    await regenerateShopping(false);
    toast(`${result.message} ✓`);
  } catch (error) { toast(error.message, "error"); }
}

async function unassign() {
  try {
    const result = await api("/api/plan", {
      method: "POST",
      body: JSON.stringify({ day: $("#assignDay").value, slot: $("#assignSlot").value, recipe_id: null }),
    });
    state.plan = result.plan;
    $("#assignModal").hidden = true;
    renderPlanner();
    await refreshNutrition();
    await regenerateShopping(false);
    toast(result.message);
  } catch (error) { toast(error.message, "error"); }
}

/* ---------------------------- Shopping list ----------------------------- */
function renderShopping(data) {
  const categories = Object.keys(data.grouped).sort();
  $("#shoppingProgress").textContent = `${data.checked} / ${data.total}`;
  $("#shoppingBar").style.width = data.total ? `${(data.checked / data.total) * 100}%` : "0%";
  $("#shoppingSummary").textContent = data.total
    ? `${data.total} ingredients gathered from your weekly thali`
    : "Generate a list to start ticking items.";

  if (!data.total) {
    $("#shoppingGroups").innerHTML = `<div class="empty-state">Your grocery basket is empty. Plan a few meals, then hit <strong>Generate from my plan</strong>.</div>`;
    return;
  }

  $("#shoppingGroups").innerHTML = categories.map((category) => `
    <section class="shop-category">
      <h4>${escapeHtml(category)}</h4>
      <div class="shop-items">
        ${data.grouped[category].map((item) => `
          <label class="shop-item">
            <input type="checkbox" data-item="${item.id}" ${item.checked ? "checked" : ""}>
            <span><span class="item-name">${escapeHtml(item.item)}<span class="shop-source">${escapeHtml(item.sources || "")}</span></span></span>
            <span class="item-qty">${escapeHtml(item.qty || "")}</span>
          </label>`).join("")}
      </div>
    </section>`).join("");

  $$("#shoppingGroups input[type=checkbox]").forEach((checkbox) =>
    checkbox.addEventListener("change", async () => {
      try {
        await api(`/api/shopping/${checkbox.dataset.item}`, {
          method: "PATCH", body: JSON.stringify({ checked: checkbox.checked }),
        });
        const fresh = await api("/api/shopping");
        $("#shoppingProgress").textContent = `${fresh.checked} / ${fresh.total}`;
        $("#shoppingBar").style.width = `${(fresh.checked / fresh.total) * 100}%`;
      } catch (error) { toast(error.message, "error"); }
    }));
}

async function regenerateShopping(notify = true) {
  try {
    await api("/api/shopping/generate", { method: "POST", body: "{}" });
    renderShopping(await api("/api/shopping"));
    if (notify) toast("Grocery list refreshed from your weekly plan ⚡");
  } catch (error) { toast(error.message, "error"); }
}

/* --------------------------- Typing hero effect ------------------------- */
function startTyping() {
  const phrases = [
    "Dal Tadka & Jeera Rice…",
    "Jaunpuri Imarti for the festive soul…",
    "Sattu Litti Chokha, straight from Purvanchal…",
    "High-protein Paneer Tikka Bowl…",
  ];
  let phraseIndex = 0, charIndex = 0, deleting = false;
  const target = $("#typedText");
  if (!target) return;
  function tick() {
    const phrase = phrases[phraseIndex];
    charIndex += deleting ? -1 : 1;
    target.textContent = phrase.slice(0, charIndex);
    if (!deleting && charIndex === phrase.length) { deleting = true; return setTimeout(tick, 1700); }
    if (deleting && charIndex === 0) { deleting = false; phraseIndex = (phraseIndex + 1) % phrases.length; return setTimeout(tick, 350); }
    setTimeout(tick, deleting ? 32 : 62);
  }
  tick();
}

/* --------------------------------- Events ------------------------------- */
function wireEvents() {
  $("#recipeSearch").addEventListener("input", (event) => {
    state.search = event.target.value;
    renderRecipes();
  });
  $("#assignFromModalBtn").addEventListener("click", () => {
    const id = state.modalRecipeId;
    openAssign(state.selectedDay, "lunch", id);
    $("#assignRecipe").value = String(id);
  });
  $("#confirmAssignBtn").addEventListener("click", confirmAssign);
  $("#unassignBtn").addEventListener("click", unassign);
  $("#generateListBtn").addEventListener("click", () => regenerateShopping(true));
  $("#openCustomRecipeBtn").addEventListener("click", () => { $("#customModal").hidden = false; });

  $$('[data-close-modal]').forEach((button) => button.addEventListener("click", () => {
    button.closest(".modal-backdrop").hidden = true;
  }));
  $$(".modal-backdrop").forEach((backdrop) => backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) backdrop.hidden = true;
  }));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") $$(".modal-backdrop").forEach((modal) => { modal.hidden = true; });
  });

  $("#customRecipeForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    const payload = Object.fromEntries(form.entries());
    try {
      const result = await api("/api/recipes", { method: "POST", body: JSON.stringify(payload) });
      state.recipes = (await api("/api/recipes")).recipes;
      renderFilters();
      renderRecipes();
      $("#customModal").hidden = true;
      event.target.reset();
      toast(`${result.recipe.name} added to your vault ✅`);
    } catch (error) { toast(error.message, "error"); }
  });

  $("#clearPlanBtn").addEventListener("click", async () => {
    if (!window.confirm("Clear all meals from this week's planner?")) return;
    try {
      await api("/api/plan", { method: "DELETE" });
      state.plan = {};
      renderPlanner();
      await refreshNutrition();
      await regenerateShopping(false);
      toast("Weekly planner cleared");
    } catch (error) { toast(error.message, "error"); }
  });

  $("#clearShoppingBtn").addEventListener("click", async () => {
    try {
      await api("/api/shopping/clear", { method: "POST", body: "{}" });
      renderShopping(await api("/api/shopping"));
      toast("Grocery list cleared");
    } catch (error) { toast(error.message, "error"); }
  });

  const params = new URLSearchParams(window.location.search);
  const view = params.get("view");
  if (view === "recipes" || window.location.hash === "#recipes") {
    state.scrollToRecipes = true;
  }
}

/* ---------------------------------- Boot -------------------------------- */
async function init() {
  wireEvents();
  renderDayPicker();
  renderFilters();
  startTyping();
  try {
    const [recipes, plan, shopping] = await Promise.all([
      api("/api/recipes"), api("/api/plan"), api("/api/shopping"),
    ]);
    state.recipes = recipes.recipes;
    state.plan = plan.plan;
    renderPlanner();
    renderWeekTotals(plan);
    renderRecipes();
    await refreshNutrition();
    renderShopping(shopping);
    if (state.scrollToRecipes) {
      requestAnimationFrame(() => {
        document.getElementById("recipes")?.scrollIntoView({ block: "start" });
        window.scrollBy(0, -70);
      });
    }
  } catch (error) {
    toast(`Could not load data: ${error.message}`, "error");
  }
}

document.addEventListener("DOMContentLoaded", init);
