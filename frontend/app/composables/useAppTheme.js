/**
 * SPARC UI Design System Composable
 * This central engine manages all CSS classes for the application.
 * Structure:
 * 1. Layout: Static structural definitions (Grids, Spacings, Shapes).
 * 2. Colors: Dynamic color mappings reacting to Dark/Light mode.
 * 3. Theme: The final computed object used directly in templates.
 * 4. getBadgeColor: Logic for dynamic status/priority styling.
 */

import { computed } from 'vue'
import { useTheme } from '~/composables/useTheme'

export const useAppTheme = () => {
  const { isDarkMode, toggleDarkMode } = useTheme()

  // --- SECTION 1: STATIC LAYOUT DEFINITIONS ---
  // These define the structure, typography, and shapes regardless of the color scheme.
  const layout = {
    // Global container constraints
    pageWidth: 'max-w-6xl mx-auto p-6',

    // CSS Grid Column Definitions for various overview pages
    gridRes:         'grid grid-cols-[1.5fr,1fr,1fr,1fr,100px] gap-3 items-center',
    gridOrders:      'grid grid-cols-[1.5fr,0.8fr,0.8fr,1fr,1fr,0.8fr,100px] gap-3 items-center',
    gridDisruptions: 'grid grid-cols-[1.2fr,0.8fr,1fr,1fr,1fr,0.8fr,100px] gap-3 items-center',
    gridWorkers:     'grid grid-cols-[1.5fr,1fr,120px] gap-3 items-center',
    gridForm:        'grid grid-cols-1 sm:grid-cols-2 gap-4',
    gridProcessSteps:'grid grid-cols-[30px_30px_1fr_1fr_1fr_130px] gap-3 items-start',

    // Structural UI Shapes
    cardShape:     'rounded-xl border p-4 space-y-4 shadow-lg transition-colors',
    rowShape:      'rounded-lg border p-3 text-sm transition-all',
    navLinkShape:  'w-full px-3 py-2 text-left rounded-lg border text-sm font-medium transition-all duration-200 shadow-sm',
    badgeShape:    'px-2 py-1 rounded-full text-xs font-semibold inline-block shadow-sm',
    totalBadgeShape: 'px-3 py-1 rounded-full text-xs font-semibold border',
    inputShape:    'w-full mt-1 px-3 py-2 rounded-lg border text-sm transition-all outline-none focus:ring-1',

    // Typography & Button Logic
    headerFont:     'px-3 py-2 text-xs font-medium uppercase tracking-wider border-b',
    headerLink:     'w-full flex items-center gap-1 hover:text-pink-500 transition-colors',
    labelFont:      'text-xs font-bold uppercase tracking-widest',
    actionBtnShape: 'px-2 py-1.5 text-xs font-medium rounded border transition-colors w-full text-center'
  }

  // --- SECTION 2: DYNAMIC COLOR PALETTE ---
  // Reactive mappings that switch classes based on the Dark Mode state.
  const colors = computed(() => ({
    // Base backgrounds & cards
    wrapper:    isDarkMode.value ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900',
    card:       isDarkMode.value ? 'border-gray-700 bg-slate-900 shadow-black' : 'border-slate-200 bg-white shadow-slate-200',

    // Tables & Lists
    headerText: isDarkMode.value
        ? 'text-slate-400 border-gray-700'
        : 'text-slate-600 border-slate-200',
    row: isDarkMode.value
      ? 'border-gray-700 bg-slate-800/50 hover:bg-slate-800'
      : 'border-slate-300 bg-slate-50 hover:bg-white hover:shadow-sm',
    totalBadge: isDarkMode.value
      ? 'border-slate-700 text-slate-400 bg-slate-800'
      : 'border-slate-300 text-slate-600 bg-slate-50',


    // Form Inputs & Labels
    input: isDarkMode.value
      ? 'bg-slate-800 border-gray-700 text-slate-100 focus:border-pink-500 focus:ring-pink-500'
      : 'bg-white border-slate-300 text-slate-900 focus:border-indigo-600 focus:ring-indigo-600',
    inputDisabled: isDarkMode.value
      ? 'bg-slate-900/50 text-slate-500 border-gray-800'
      : 'bg-slate-100 text-slate-600 border-slate-300',
    label: isDarkMode.value
        ? 'text-slate-400'
        : 'text-slate-600',

    // Navigation specific colors
    navActive:   'bg-gradient-to-r from-indigo-600 to-pink-600 text-white border-transparent shadow-indigo-500/20',
    navInactive: isDarkMode.value
      ? 'border-gray-700 bg-gray-800/40 text-slate-300 hover:bg-gray-700 hover:text-white'
      : 'border-slate-300 bg-slate-50 text-slate-700 hover:bg-white hover:text-indigo-700',

    // Generic Buttons
    btnDeleteMode: isDarkMode.value
      ? 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700'
      : 'bg-white text-slate-800 border-slate-300 hover:bg-slate-50',
    btnDeleteModeActive: isDarkMode.value
      ? 'bg-slate-700 text-white border-slate-600'
      : 'bg-slate-700 text-white border-slate-600',

    btnAction: isDarkMode.value
      ? 'border-gray-600 text-slate-300 hover:bg-indigo-900/30 hover:text-indigo-300 hover:border-indigo-800'
      : 'border-slate-300 text-slate-700 hover:bg-white hover:text-indigo-700 hover:border-indigo-300',
    btnActionDelete: isDarkMode.value
      ? 'border-red-800 text-red-400 hover:bg-red-900/30'
      : 'border-red-200 text-red-500 hover:bg-red-50',

    // --- Popout / Floating Panel ---
    popoutContainer: isDarkMode.value
      ? 'border-slate-800 bg-slate-950 text-slate-100'
      : 'border-slate-200 bg-white text-slate-900',
    popoutHeader: isDarkMode.value
      ? 'border-slate-800 bg-slate-900 text-white'
      : 'border-slate-200 bg-slate-50 text-slate-800',
    popoutBtnSecondary: isDarkMode.value
      ? 'border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50',

    // --- File Upload ---
    fileUploadBtn: isDarkMode.value
      ? 'border-gray-700 bg-gray-800 text-slate-200 hover:bg-gray-700'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
    fileRow: isDarkMode.value
      ? 'border-gray-700 bg-gray-800'
      : 'border-slate-200 bg-slate-50',
    fileNameText: isDarkMode.value ? 'text-slate-200' : 'text-slate-700',
    fileMetaText: isDarkMode.value ? 'text-slate-400' : 'text-slate-500',
    fileViewBtn: isDarkMode.value
      ? 'border-gray-600 text-slate-300 hover:bg-gray-700'
      : 'border-slate-300 text-slate-600 hover:bg-slate-100',
    fileDeleteBtn: isDarkMode.value
      ? 'border-red-900 text-red-400 hover:bg-red-900/30'
      : 'border-red-200 text-red-600 hover:bg-red-50',
    fileEmptyState: isDarkMode.value
      ? 'border-gray-700 text-slate-400'
      : 'border-slate-300 text-slate-500',

    // --- MultiSelect ---
    multiSelectContainer: isDarkMode.value
      ? 'border-gray-700 bg-gray-800'
      : 'border-slate-300 bg-white',
    multiSelectFocus: isDarkMode.value
      ? 'ring-1 ring-pink-500 border-pink-500'
      : 'ring-1 ring-indigo-500 border-indigo-500',
    multiSelectTag: isDarkMode.value
      ? 'bg-gray-700 border-gray-600 text-slate-200'
      : 'bg-indigo-50 border-indigo-100 text-indigo-700',
    multiSelectInput: isDarkMode.value
      ? 'text-slate-100 placeholder-slate-500'
      : 'text-slate-900 placeholder-slate-400',
    multiSelectDropdown: isDarkMode.value
      ? 'bg-gray-800 border-gray-700'
      : 'bg-white border-slate-200',
    multiSelectOption: isDarkMode.value
      ? 'text-slate-200 hover:bg-gray-700'
      : 'text-slate-700 hover:bg-slate-100',

    // --- Timer Display ---
    timerDisplay: isDarkMode.value
      ? 'bg-gray-800 text-green-400 border border-gray-700'
      : 'bg-slate-100 text-green-600 border border-slate-300',
    timerResetBtn: isDarkMode.value
      ? 'border-gray-700 bg-gray-800 text-slate-200 hover:bg-gray-700'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-100',

    // --- Topbar ---
    topbar: isDarkMode.value
      ? 'border-gray-600 bg-gradient-to-r from-indigo-900 via-slate-900 to-pink-900'
      : 'border-slate-200 bg-white text-slate-800 shadow-sm',
    topbarTitle: isDarkMode.value ? 'text-white' : 'text-indigo-900',
    topbarResetBtn: isDarkMode.value
      ? 'border-gray-700 bg-gray-900 text-slate-100 hover:border-pink-700'
      : 'border-slate-300 bg-white text-slate-700 hover:border-indigo-500 hover:text-indigo-600',

    // --- Zoom / small utility buttons ---
    zoomBtn: isDarkMode.value
      ? 'border-slate-600'
      : 'border-slate-300/70',

    // Status indicator dot
    modeIndicator: isDarkMode.value ? 'bg-indigo-500' : 'bg-amber-500',

    // --- Dashboard ---
    dashboardSubtitle: isDarkMode.value ? 'text-slate-300' : 'text-slate-500',
    dashboardHint: isDarkMode.value ? 'text-slate-400' : 'text-slate-500',
    dashboardPanel: isDarkMode.value
      ? 'border-gray-700 bg-slate-900 shadow-black'
      : 'border-slate-200 bg-white shadow-slate-200',
    dashboardPanelRow: isDarkMode.value
      ? 'border-gray-700 bg-gray-700'
      : 'border-slate-200 bg-slate-50',
    dashboardPanelHeaderBorder: isDarkMode.value
      ? 'border-gray-700 text-slate-100'
      : 'border-slate-200 text-slate-900',
    dashboardEditBtn: isDarkMode.value
      ? 'border-gray-600 hover:bg-gray-700 text-slate-200'
      : 'border-slate-300 hover:bg-slate-200 text-slate-700',
    dashboardOpenLink: isDarkMode.value
      ? 'text-pink-200 hover:text-pink-100'
      : 'text-pink-600 hover:text-pink-800',
    dashboardDragHint: isDarkMode.value ? 'text-slate-400' : 'text-slate-500',
    dashboardEditRing: isDarkMode.value ? 'ring-2 ring-pink-500' : 'ring-2 ring-indigo-400',
    dashboardChartBg: isDarkMode.value
      ? 'border-gray-700 bg-gray-800'
      : 'border-slate-200 bg-slate-50',
    dashboardAxisStroke: isDarkMode.value ? '#475569' : '#cbd5f5',
    dashboardAxisText: isDarkMode.value ? '#94a3b8' : '#64748b',
    dashboardBarFill: isDarkMode.value ? '#f472b6' : '#6366f1',
    dashboardMetaText: isDarkMode.value ? 'text-slate-300' : 'text-slate-500',
    dashboardEmptyChart: isDarkMode.value ? 'text-slate-400' : 'text-slate-500',

    // --- Info box (notes) ---
    infoBox: isDarkMode.value
      ? 'bg-slate-800/50 border-slate-700'
      : 'bg-slate-500/5 border-slate-500/10'
  }))

  // --- SECTION 3: UNIFIED THEME OBJECT ---
  // This combines Layout and Colors into final class strings for templates.
  const theme = computed(() => ({
    // Global Wrappers
    pageWrapper: `min-h-screen transition-colors duration-300 ${colors.value.wrapper}`,
    container:   layout.pageWidth,
    card:        `${layout.cardShape} ${colors.value.card}`,

    // Sidebar & Navigation Component
    sidebar:         `w-64 border-l p-4 flex flex-col gap-2 transition-colors duration-300 ${colors.value.card}`,
    navLabel:        `${layout.labelFont} mb-2 ${colors.value.label}`,
    navLinkActive:   `${layout.navLinkShape} ${colors.value.navActive}`,
    navLinkInactive: `${layout.navLinkShape} ${colors.value.navInactive}`,
    navFooter:       `mt-auto pt-4 border-t text-[10px] uppercase tracking-widest ${isDarkMode.value ? 'border-gray-700 text-slate-500' : 'border-slate-200 text-slate-400'}`,

    // Dynamic Table Grids (Header & Row variants)
    tableHeaderRes:         `${layout.gridRes} ${layout.headerFont} ${colors.value.headerText}`,
    tableRowRes:            `${layout.gridRes} ${layout.rowShape} ${colors.value.row}`,
    tableHeaderOrders:      `${layout.gridOrders} ${layout.headerFont} ${colors.value.headerText}`,
    tableRowOrders:         `${layout.gridOrders} ${layout.rowShape} ${colors.value.row}`,
    tableHeaderDisruptions: `${layout.gridDisruptions} ${layout.headerFont} ${colors.value.headerText}`,
    tableRowDisruptions:    `${layout.gridDisruptions} ${layout.rowShape} ${colors.value.row}`,
    tableHeaderWorkers:     `${layout.gridWorkers} ${layout.headerFont} ${colors.value.headerText}`,
    tableRowWorkers:        `${layout.gridWorkers} ${layout.rowShape} ${colors.value.row}`,

    // Form & Input Elements
    formGrid:        layout.gridForm,
    processStepGrid: layout.gridProcessSteps,
    input:           `${layout.inputShape} ${colors.value.input}`,
    inputDisabled:   `${layout.inputShape} ${colors.value.inputDisabled}`,
    label:           `${layout.labelFont} ${colors.value.label}`,
    headerBtn:       layout.headerLink,

    // Buttons & Badges
    badge:         layout.badgeShape,
    totalBadge:    `${layout.totalBadgeShape} ${colors.value.totalBadge}`,
    btnDeleteMode: `px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm ${colors.value.btnDeleteMode}`,
    btnDeleteModeActive: `px-3 py-2 rounded-lg text-sm font-semibold border transition-all shadow-sm ${colors.value.btnDeleteModeActive}`,
    btnAction:     `${layout.actionBtnShape} ${colors.value.btnAction}`,
    btnActionDelete: `${layout.actionBtnShape} ${colors.value.btnActionDelete}`,
    btnWarning:    'px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-amber-500 to-red-600 shadow-md hover:brightness-110 transition-all',
    btnNewEntity:  'px-3 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-pink-500 shadow-md hover:shadow-lg hover:brightness-110 transition-all',
    btnConfirmDelete: 'bg-red-600 text-white text-[10px] font-bold uppercase px-2 py-1 rounded animate-pulse shadow-sm',
    linkAction:    `text-sm font-semibold hover:underline ${isDarkMode.value ? 'text-pink-300' : 'text-pink-600'}`,

    // --- Popout / Floating Panel ---
    popoutContainer: `fixed z-50 w-72 overflow-hidden rounded-xl border shadow-lg select-none ${colors.value.popoutContainer}`,
    popoutHeader:    `cursor-move px-4 py-3 border-b font-semibold text-sm tracking-wide ${colors.value.popoutHeader}`,
    popoutBtnSecondary: `rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0 ${colors.value.popoutBtnSecondary}`,

    // --- File Upload ---
    fileUploadBtn:  `px-3 py-1.5 text-xs rounded-lg border transition-colors font-medium ${colors.value.fileUploadBtn}`,
    fileRow:        `flex items-center justify-between p-3 rounded-lg border text-sm transition-colors ${colors.value.fileRow}`,
    fileNameText:   `font-medium truncate ${colors.value.fileNameText}`,
    fileMetaText:   `text-xs ${colors.value.fileMetaText}`,
    fileViewBtn:    `px-2 py-1 text-xs rounded border transition-colors ${colors.value.fileViewBtn}`,
    fileDeleteBtn:  `px-2 py-1 text-xs rounded border transition-colors ${colors.value.fileDeleteBtn}`,
    fileEmptyState: `p-4 rounded-lg border-2 border-dashed text-center ${colors.value.fileEmptyState}`,

    // --- MultiSelect ---
    multiSelectContainer: `min-h-[40px] w-full rounded-lg border px-2 py-1.5 flex flex-wrap gap-2 items-center cursor-text transition-colors ${colors.value.multiSelectContainer}`,
    multiSelectFocus:     colors.value.multiSelectFocus,
    multiSelectTag:       `inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium border ${colors.value.multiSelectTag}`,
    multiSelectInput:     `flex-1 min-w-[60px] bg-transparent outline-none text-sm ${colors.value.multiSelectInput}`,
    multiSelectDropdown:  `absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border shadow-lg py-1 ${colors.value.multiSelectDropdown}`,
    multiSelectOption:    `px-3 py-2 text-sm cursor-pointer transition-colors ${colors.value.multiSelectOption}`,

    // --- Timer ---
    timerDisplay:  `px-4 py-2 rounded-lg font-mono text-lg font-bold ${colors.value.timerDisplay}`,
    timerResetBtn: `px-3 py-2 rounded-lg text-sm font-semibold border transition-colors ${colors.value.timerResetBtn}`,

    // --- Topbar ---
    topbar:        `flex items-center justify-between border-b px-6 py-4 transition-colors duration-300 ${colors.value.topbar}`,
    topbarTitle:   `font-semibold tracking-[0.12em] uppercase ${colors.value.topbarTitle}`,
    topbarResetBtn:`rounded-lg border px-3 py-2 text-sm transition-colors ${colors.value.topbarResetBtn}`,
    topbarSubmitBtn: 'rounded-lg px-3 py-2 text-sm font-semibold text-white disabled:opacity-40 transition-all shadow-md',
    topbarSubmitActive: 'bg-gradient-to-r from-indigo-500 to-pink-500',
    topbarSubmitDisabled: 'bg-gray-500',

    // --- Zoom buttons ---
    zoomBtn: `px-2 py-1 rounded border ${colors.value.zoomBtn}`,

    // --- Status indicator ---
    modeIndicator: `w-1.5 h-1.5 rounded-full ${colors.value.modeIndicator}`,

    // --- Dashboard ---
    dashboardCard:       `rounded-xl border p-4 shadow-lg transition-colors ${colors.value.dashboardPanel}`,
    dashboardSubtitle:   `text-sm font-semibold uppercase tracking-[0.2em] ${colors.value.dashboardSubtitle}`,
    dashboardHint:       `text-xs mt-1 ${colors.value.dashboardHint}`,
    dashboardEditBtn:    `px-3 py-2 text-sm rounded-lg border transition-colors ${colors.value.dashboardEditBtn}`,
    dashboardPanel:      colors.value.dashboardPanel,
    dashboardPanelRow:   `rounded-lg border px-3 py-2 text-sm ${colors.value.dashboardPanelRow}`,
    dashboardOpenLink:   `text-xs font-medium ${colors.value.dashboardOpenLink}`,
    dashboardDragHint:   `text-xs ${colors.value.dashboardDragHint}`,
    dashboardEditRing:   colors.value.dashboardEditRing,
    dashboardHeaderText: `text-xs ${colors.value.dashboardHint}`,
    dashboardChartBg:    `rounded-lg border px-3 py-3 ${colors.value.dashboardChartBg}`,
    dashboardMetaText:   `text-xs ${colors.value.dashboardMetaText}`,
    dashboardEmptyChart: `text-xs ${colors.value.dashboardEmptyChart}`,

    // --- Info box ---
    infoBox: `p-3 rounded-lg border text-xs opacity-70 leading-relaxed ${colors.value.infoBox}`
  }))

  // --- SECTION 4: HELPER FUNCTIONS ---
  /**
   * Returns specific Tailwind color classes for badges based on status or type.
   * @param {string} kind - The category of the badge (status, priority, disruption).
   * @param {string} valueStr - The text value to map.
   */
  const getBadgeColor = (kind, valueStr) => {
    const tones = {
      // Order & Process Status
      Running: 'bg-emerald-600 text-emerald-100',
      Planned: 'bg-blue-600 text-blue-100',
      Paused:  'bg-amber-600 text-amber-100',
      Done:    'bg-slate-600 text-slate-100',

      // Priorities
      High:   'bg-pink-600 text-pink-100',
      Medium: 'bg-indigo-600 text-indigo-100',
      Low:    'bg-slate-600 text-slate-100',

      // Resource Status
      Offline:     'bg-red-600 text-red-100',
      'In Use':    'bg-indigo-600 text-indigo-100',
      Available:   'bg-emerald-600 text-emerald-100',
      Maintenance: 'bg-amber-600 text-amber-100',

      // Disruption Types
      Breakdown:   'bg-red-600 text-red-100',
      Warning:     'bg-amber-600 text-amber-100',
      Information: 'bg-blue-600 text-blue-100'
    }
    return tones[valueStr] || 'bg-slate-600 text-slate-100'
  }

  return {
    theme,
    colors,
    isDarkMode,
    toggleDarkMode,
    getBadgeColor
  }
}