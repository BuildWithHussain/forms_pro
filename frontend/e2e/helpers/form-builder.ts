import type { Locator, Page } from "@playwright/test";

export class FormBuilderPage {
  constructor(private page: Page) {}

  // ---- Layout introspection helpers ----

  fieldCard(label: string): Locator {
    return this.page.locator(
      `[data-form-builder-component="field-card"][data-field-label="${label}"]`
    );
  }

  // Wait for the builder to finish hydrating with the form's fields (the
  // form fetch is async after navigation; helps avoid races when tests load
  // pre-built layouts via the REST API).
  async waitForFields(labels: string[]) {
    for (const label of labels) {
      await this.fieldCard(label).waitFor({ state: "visible", timeout: 15000 });
    }
  }

  async rowCount(): Promise<number> {
    return this.page
      .locator('[data-form-builder-component="form-row"]')
      .count();
  }

  async columnCount(rowIdx: number): Promise<number> {
    return this.page
      .locator(
        `[data-form-builder-component="cell-column"][data-row-index="${rowIdx}"]`
      )
      .count();
  }

  async cellCount(rowIdx: number, colIdx: number): Promise<number> {
    return this.page
      .locator(
        `[data-form-builder-component="field-card"][data-row-index="${rowIdx}"][data-col-index="${colIdx}"]`
      )
      .count();
  }

  // ---- Drag mechanics ----
  // SortableJS + Playwright is fragile. Use a real mouse path with intermediate
  // steps so SortableJS sees a continuous dragover sequence.
  private async dragWithRealMouse(
    sourceHandle: Locator,
    targetCenter: { x: number; y: number },
    waypoints: { x: number; y: number }[] = []
  ) {
    const handleBox = await sourceHandle.boundingBox();
    if (!handleBox) throw new Error("source handle not visible");

    const start = {
      x: handleBox.x + handleBox.width / 2,
      y: handleBox.y + handleBox.height / 2,
    };

    await this.page.mouse.move(start.x, start.y);
    await this.page.mouse.down();
    // Small initial nudge — SortableJS needs movement to begin drag
    await this.page.mouse.move(start.x + 4, start.y + 4, { steps: 4 });

    // Walk through caller-supplied waypoints (lets the path avoid crossing
    // other sortable instances en route). Each leg uses many steps so
    // SortableJS receives a continuous dragover/pointer-move sequence.
    let prev = start;
    for (const wp of waypoints) {
      await this.page.mouse.move(wp.x, wp.y, { steps: 10 });
      prev = wp;
    }

    // Approach the target with a midpoint then arrival
    await this.page.mouse.move(
      (prev.x + targetCenter.x) / 2,
      (prev.y + targetCenter.y) / 2,
      { steps: 10 }
    );
    await this.page.mouse.move(targetCenter.x, targetCenter.y, { steps: 12 });

    // Wiggle at target — forces a fresh dragover/pointer-move sequence on
    // the final drop target so SortableJS commits the swap there, not
    // somewhere we crossed earlier in the path.
    await this.page.waitForTimeout(80);
    await this.page.mouse.move(targetCenter.x + 2, targetCenter.y + 2, {
      steps: 4,
    });
    await this.page.mouse.move(targetCenter.x, targetCenter.y, { steps: 4 });
    await this.page.waitForTimeout(120);
    await this.page.mouse.up();
  }

  private dragHandle(card: Locator): Locator {
    return card.locator(".handle");
  }

  async dragFieldOntoCell(
    sourceLabel: string,
    targetLabel: string,
    position: "above" | "below"
  ) {
    const source = this.fieldCard(sourceLabel);
    const target = this.fieldCard(targetLabel);

    // Hover the target's group first so its handle/actions render (needed for
    // the source handle to be visible — actions only show on hover/select).
    await source.hover();
    const handle = this.dragHandle(source);
    await handle.waitFor({ state: "visible" });

    const sourceBox = await source.boundingBox();
    const box = await target.boundingBox();
    if (!sourceBox) throw new Error(`source card '${sourceLabel}' not visible`);
    if (!box) throw new Error(`target card '${targetLabel}' not visible`);

    // Position cursor in upper / lower portion of target card
    const yOffset =
      position === "above" ? box.height * 0.25 : box.height * 0.75;
    const targetCenter = {
      x: box.x + box.width / 2,
      y: box.y + yOffset,
    };

    // If the drag crosses rows, route through a waypoint that lives in the
    // row drop zone between rows. This avoids accidentally swapping into
    // another sortable instance (e.g. the neighbouring column in the source
    // row) while passing through. Detect cross-row by comparing the cards'
    // data-row-index attributes, which is robust to drop-zone size changes
    // (a y-distance heuristic broke once RowDropZone shrank from h-6 to
    // h-3, because adjacent rows became close enough that the vertical gap
    // was smaller than a card's height).
    const waypoints: { x: number; y: number }[] = [];
    const sourceMidY = sourceBox.y + sourceBox.height / 2;
    const sourceRow = Number(
      (await source.getAttribute("data-row-index")) ?? 0
    );
    const targetRow = Number(
      (await target.getAttribute("data-row-index")) ?? 0
    );
    const isCrossRow = sourceRow !== targetRow;
    if (isCrossRow) {
      // Pick the row-drop-zone whose centre lies in the vertical band
      // between source and target — robust to duplicate data-at-row values
      // and to changes in the zone's visual height.
      const lo = Math.min(sourceMidY, targetCenter.y);
      const hi = Math.max(sourceMidY, targetCenter.y);
      let transitY = (sourceMidY + targetCenter.y) / 2;
      const zones = await this.page
        .locator('[data-form-builder-component="row-drop-zone"]')
        .all();
      for (const z of zones) {
        const zb = await z.boundingBox();
        if (!zb) continue;
        const zMid = zb.y + zb.height / 2;
        if (zMid > lo && zMid < hi) {
          transitY = zMid;
          break;
        }
      }
      // Drop straight down (or up) along the source's x first so we leave
      // the source's row through the row drop zone, then slide horizontally
      // toward the target before approaching.
      waypoints.push({
        x: sourceBox.x + sourceBox.width / 2,
        y: transitY,
      });
      waypoints.push({ x: targetCenter.x, y: transitY });
    }

    await this.dragWithRealMouse(handle, targetCenter, waypoints);
  }

  // Drag a field onto a ColumnDropZone (gap between/around columns within a row).
  // Targets the zone with [data-at-row=atRow][data-at-col=atCol].
  async dragFieldToColumnZone(
    sourceLabel: string,
    atRow: number,
    atCol: number
  ) {
    const source = this.fieldCard(sourceLabel);
    await source.hover();
    const handle = this.dragHandle(source);
    await handle.waitFor({ state: "visible" });

    const zone = this.page.locator(
      `[data-form-builder-component="column-drop-zone"][data-at-row="${atRow}"][data-at-col="${atCol}"]`
    );
    const box = await zone.boundingBox();
    if (!box) {
      throw new Error(`column drop zone (${atRow},${atCol}) not visible`);
    }

    await this.dragWithRealMouse(handle, {
      x: box.x + box.width / 2,
      y: box.y + box.height / 2,
    });
  }

  // Click the eject button on the field's card (action bar).
  // Action bar only mounts visible on hover/select — hover first.
  async ejectField(label: string) {
    const card = this.fieldCard(label);
    await card.hover();
    const ejectBtn = card.locator(
      '[data-form-builder-component="eject-button"]'
    );
    await ejectBtn.waitFor({ state: "visible" });
    await ejectBtn.click();
  }

  // Drag a field onto a RowDropZone above row atRow.
  async dragFieldToRowZone(sourceLabel: string, atRow: number) {
    const source = this.fieldCard(sourceLabel);
    await source.hover();
    const handle = this.dragHandle(source);
    await handle.waitFor({ state: "visible" });

    const zone = this.page.locator(
      `[data-form-builder-component="row-drop-zone"][data-at-row="${atRow}"]`
    );
    const box = await zone.boundingBox();
    if (!box) throw new Error(`row drop zone at row ${atRow} not visible`);

    await this.dragWithRealMouse(handle, {
      x: box.x + box.width / 2,
      y: box.y + box.height / 2,
    });
  }

  async goto(
    formId: string,
    options?: { title?: string; skipTitleFill?: boolean }
  ) {
    await this.page.goto(`/forms/edit-form/${formId}`);
    // Wait for the sidebar to confirm the builder is mounted
    await this.page.waitForSelector(
      '[data-form-builder-component="form-builder-sidebar"]'
    );

    if (options?.skipTitleFill) return;

    // Set unique title to avoid MandatoryError on save (frontend transforms "Untitled Form" → "")
    const title = options?.title ?? `E2E Form ${Date.now()}`;
    await this.page.getByPlaceholder("Untitled Form").fill(title);

    // Save immediately so form is clean and Publish/Unpublish button shows
    const saveBtn = this.page.getByRole("button", {
      name: "Save",
      exact: true,
    });
    // Wait briefly for dirty state to propagate
    await this.page.waitForTimeout(200);
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
      await saveBtn.waitFor({ state: "hidden", timeout: 30000 });
    }
  }

  // Scope selectors to the sidebar (which has a stable pre-existing attribute)
  private sidebar() {
    return this.page.locator(
      '[data-form-builder-component="form-builder-sidebar"]'
    );
  }

  async addField(fieldType: string) {
    await this.sidebar()
      .getByRole("button", { name: fieldType, exact: true })
      .click();
  }

  // The canvas shows "Click on fields to add them…" when empty
  canvasEmptyState() {
    return this.page.getByText(/click on fields to add them/i);
  }

  async publish() {
    // After edits, form is dirty — header shows "Save" instead of "Publish".
    // Save first so the Publish button becomes available.
    const saveBtn = this.page.getByRole("button", {
      name: "Save",
      exact: true,
    });
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
      // Wait for Save to disappear — same render cycle as Publish appearing
      await saveBtn.waitFor({ state: "hidden", timeout: 30000 });
    }
    await this.page.getByRole("button", { name: /^publish$/i }).click();
    await this.page
      .getByRole("button", { name: /^unpublish$/i })
      .waitFor({ timeout: 10000 });
  }

  async unpublish() {
    await this.page.getByRole("button", { name: /^unpublish$/i }).click();
    await this.page
      .getByRole("button", { name: /^publish$/i })
      .waitFor({ timeout: 10000 });
  }

  publishButton() {
    return this.page.getByRole("button", { name: /^publish$/i });
  }

  // ---- Step navigation (SectionNavBar) ----

  stepNav(): Locator {
    return this.page.locator('nav[aria-label="Form steps"]');
  }

  stepTab(label: string): Locator {
    return this.stepNav().getByRole("button", { name: label, exact: true });
  }

  activeStepTab(): Locator {
    return this.stepNav().locator('button[aria-current="true"]');
  }

  async addStep() {
    await this.stepNav().getByRole("button", { name: "Add Step" }).click();
  }

  async switchToStep(label: string) {
    await this.stepTab(label).click();
  }

  async renameStep(oldLabel: string, newLabel: string) {
    await this.stepTab(oldLabel).dblclick();
    const input = this.stepNav().getByRole("textbox");
    await input.waitFor({ state: "visible" });
    await input.fill(newLabel);
    await input.press("Enter");
  }

  // mode "keep"  -> "Move fields to previous step"
  // mode "delete"-> "Remove step and fields"
  // omit mode for empty steps (no dialog appears)
  async removeStep(label: string, mode?: "keep" | "delete") {
    const tab = this.stepTab(label);
    await tab.hover();
    await tab.getByLabel("Remove step").click();
    if (mode === "keep") {
      await this.page
        .getByRole("button", { name: "Move fields to previous step" })
        .click();
    } else if (mode === "delete") {
      await this.page
        .getByRole("button", { name: "Remove step and fields" })
        .click();
    }
  }

  async save() {
    const saveBtn = this.page.getByRole("button", {
      name: "Save",
      exact: true,
    });
    await saveBtn.click();
    await saveBtn.waitFor({ state: "hidden", timeout: 30000 });
  }
}
