#!/usr/bin/env python3
"""
Dragon Warrior Interactive Map Generator
Creates an interactive HTML map viewer with encounter zones and warp points
"""

import json
from pathlib import Path

# Warp points from Bank03.asm MapTargetTbl (LF461-LF4F7)
WARP_POINTS = [
	{"from_x": 2, "from_y": 2, "to": "Garinham", "name": "Garinham Cave Entrance"},
	{"from_x": 81, "from_y": 1, "to": "Staff of Rain Cave", "name": "Rain Cave"},
	{"from_x": 104, "from_y": 10, "to": "Kol", "name": "Town of Kol"},
	{"from_x": 48, "from_y": 41, "to": "Brecconary", "name": "Town of Brecconary"},
	{"from_x": 43, "from_y": 43, "to": "Tantegel Castle", "name": "Tantegel Castle"},
	{"from_x": 104, "from_y": 44, "to": "Swamp Cave", "name": "Swamp Cave North"},
	{"from_x": 48, "from_y": 48, "to": "Dragonlord's Castle", "name": "Charlock Castle"},
	{"from_x": 104, "from_y": 49, "to": "Swamp Cave", "name": "Swamp Cave South"},
	{"from_x": 29, "from_y": 57, "to": "Rock Mountain", "name": "Rock Mountain Cave"},
	{"from_x": 102, "from_y": 72, "to": "Rimuldar", "name": "Town of Rimuldar"},
	{"from_x": 25, "from_y": 89, "to": "Hauksness", "name": "Town of Hauksness"},
	{"from_x": 73, "from_y": 102, "to": "Cantlin", "name": "Town of Cantlin"},
	{"from_x": 108, "from_y": 109, "to": "Rainbow Drop Cave", "name": "Rainbow Drop"},
	{"from_x": 28, "from_y": 12, "to": "Erdrick's Cave", "name": "Erdrick's Cave"}
]

# Encounter zones (8×8 grid) from Bank03.asm OvrWrldEnGrid (LF522-LF53E)
ENCOUNTER_GRID = [
	[0x3, 0x3, 0x2, 0x2, 0x3, 0x5, 0x4, 0x5],
	[0x3, 0x2, 0x1, 0x2, 0x3, 0x3, 0x4, 0x5],
	[0x4, 0x1, 0x0, 0x0, 0x2, 0x3, 0x4, 0x5],
	[0x5, 0x1, 0x1, 0xC, 0x6, 0x6, 0x6, 0x6],
	[0x5, 0x5, 0x4, 0xC, 0x9, 0x7, 0x7, 0x7],
	[0xA, 0x9, 0x8, 0xC, 0xC, 0xC, 0x8, 0x7],
	[0xA, 0xA, 0xB, 0xC, 0xD, 0xD, 0x9, 0x8],
	[0xB, 0xB, 0xC, 0xD, 0xD, 0xC, 0x9, 0x9]
]

ENCOUNTER_NAMES = {
	0x0: "Slime/Red Slime",
	0x1: "Red Slime/Drakee",
	0x2: "Slime/Ghost/Drakee",
	0x3: "Red Slime/Drakee/Ghost/Magician",
	0x4: "Ghost/Magician/Magidrakee/Scorpion",
	0x5: "Ghost/Magician/Scorpion/Skeleton",
	0x6: "Magidrakee/Scorpion/Skeleton/Warlock/Wolf",
	0x7: "Skeleton/Warlock/Metal Scorpion/Wolf",
	0x8: "Metal Scorpion/Wraith/Wolflord/Goldman",
	0x9: "Wraith/Wyvern/Wolflord/Goldman",
	0xA: "Wyvern/Wolflord/Golem/Knight/Magiwyvern",
	0xB: "Wolflord/Golem/Knight/Magiwyvern/Demon Knight",
	0xC: "Golem/Knight/Magiwyvern/Demon Knight/Armored Knight",
	0xD: "Knight/Magiwyvern/Demon Knight/Armored Knight/Green Dragon"
}

def generate_interactive_map_html(map_json_path: str, output_html_path: str):
	"""Generate interactive HTML map viewer"""

	# Load map data
	with open(map_json_path, 'r') as f:
		map_data = json.load(f)

	width = map_data['width']
	height = map_data['height']
	tiles = map_data['tiles']

	# Generate HTML
	html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Dragon Warrior - Interactive Overworld Map</title>
	<style>
		* {{
			margin: 0;
			padding: 0;
			box-sizing: border-box;
		}}

		body {{
			font-family: 'Courier New', monospace;
			background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
			color: #fff;
			overflow: hidden;
		}}

		.container {{
			display: flex;
			height: 100vh;
		}}

		.sidebar {{
			width: 300px;
			background: rgba(0, 0, 0, 0.7);
			padding: 20px;
			overflow-y: auto;
			border-right: 2px solid #0f3460;
		}}

		.map-container {{
			flex: 1;
			position: relative;
			overflow: hidden;
			display: flex;
			align-items: center;
			justify-content: center;
		}}

		h1 {{
			color: #e94560;
			margin-bottom: 10px;
			font-size: 1.5em;
			text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
		}}

		.subtitle {{
			color: #aaa;
			margin-bottom: 20px;
			font-size: 0.8em;
		}}

		#canvas {{
			border: 2px solid #0f3460;
			cursor: move;
			image-rendering: pixelated;
			image-rendering: -moz-crisp-edges;
			image-rendering: crisp-edges;
		}}

		.controls {{
			background: rgba(15, 52, 96, 0.5);
			padding: 15px;
			border-radius: 8px;
			margin-bottom: 15px;
		}}

		.control-group {{
			margin-bottom: 10px;
		}}

		label {{
			display: block;
			color: #e94560;
			margin-bottom: 5px;
			font-weight: bold;
		}}

		input[type="range"] {{
			width: 100%;
			margin: 5px 0;
		}}

		button {{
			background: linear-gradient(135deg, #e94560 0%, #c7375a 100%);
			color: white;
			border: none;
			padding: 8px 16px;
			border-radius: 4px;
			cursor: pointer;
			font-family: 'Courier New', monospace;
			font-weight: bold;
			margin: 2px;
			transition: transform 0.1s;
		}}

		button:hover {{
			transform: scale(1.05);
			background: linear-gradient(135deg, #ff4d6d 0%, #d84663 100%);
		}}

		button:active {{
			transform: scale(0.95);
		}}

		.legend {{
			background: rgba(15, 52, 96, 0.5);
			padding: 15px;
			border-radius: 8px;
			margin-bottom: 15px;
		}}

		.legend h3 {{
			color: #e94560;
			margin-bottom: 10px;
			font-size: 1.1em;
		}}

		.legend-item {{
			display: flex;
			align-items: center;
			margin: 5px 0;
			font-size: 0.85em;
		}}

		.legend-color {{
			width: 20px;
			height: 20px;
			margin-right: 10px;
			border: 1px solid #333;
		}}

		.info {{
			background: rgba(15, 52, 96, 0.5);
			padding: 15px;
			border-radius: 8px;
			font-size: 0.85em;
		}}

		.info-item {{
			margin: 5px 0;
		}}

		.checkbox-group {{
			margin: 10px 0;
		}}

		.checkbox-group input {{
			margin-right: 5px;
		}}

		.warp-list {{
			max-height: 200px;
			overflow-y: auto;
			background: rgba(0, 0, 0, 0.3);
			padding: 10px;
			border-radius: 4px;
			font-size: 0.8em;
		}}

		.warp-item {{
			margin: 5px 0;
			padding: 5px;
			background: rgba(233, 69, 96, 0.2);
			border-left: 3px solid #e94560;
			cursor: pointer;
		}}

		.warp-item:hover {{
			background: rgba(233, 69, 96, 0.4);
		}}
	</style>
</head>
<body>
	<div class="container">
		<div class="sidebar">
			<h1>🐉 Dragon Warrior</h1>
			<div class="subtitle">Interactive Overworld Map</div>

			<div class="controls">
				<h3 style="color: #e94560; margin-bottom: 10px;">Controls</h3>

				<div class="control-group">
					<label>Zoom: <span id="zoomLevel">4x</span></label>
					<input type="range" id="zoomSlider" min="1" max="16" value="4" step="1">
				</div>

				<div class="checkbox-group">
					<label><input type="checkbox" id="showGrid" checked> Show Grid</label>
					<label><input type="checkbox" id="showWarps" checked> Show Warp Points</label>
					<label><input type="checkbox" id="showEncounters" checked> Show Encounter Zones</label>
				</div>

				<button onclick="resetView()">Reset View</button>
				<button onclick="toggleFullscreen()">Fullscreen</button>
			</div>

			<div class="legend">
				<h3>Tile Legend</h3>
				<div class="legend-item"><div class="legend-color" style="background: rgb(34, 177, 76);"></div>Grass</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(255, 217, 102);"></div>Desert</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(139, 90, 43);"></div>Hills</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(96, 96, 96);"></div>Mountain</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(0, 112, 221);"></div>Water</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(64, 64, 64);"></div>Rock Wall</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(0, 100, 0);"></div>Forest</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(128, 0, 128);"></div>Poison</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(192, 192, 192);"></div>Town</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(255, 215, 0);"></div>Castle</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(210, 180, 140);"></div>Bridge</div>
				<div class="legend-item"><div class="legend-color" style="background: rgb(255, 165, 0);"></div>Stairs/Cave</div>
			</div>

			<div class="legend">
				<h3>Warp Points</h3>
				<div class="warp-list">
"""

	# Add warp points to sidebar
	for warp in WARP_POINTS:
		html += f'                    <div class="warp-item" onclick="jumpToLocation({warp["from_x"]}, {warp["from_y"]})">\n'
		html += f'                        📍 {warp["name"]} ({warp["from_x"]},{warp["from_y"]})\n'
		html += f'                    </div>\n'

	html += """                </div>
			</div>

			<div class="info">
				<h3 style="color: #e94560; margin-bottom: 10px;">Map Info</h3>
				<div class="info-item">📏 Size: 120×120 tiles</div>
				<div class="info-item">🎮 Total Tiles: 14,400</div>
				<div class="info-item">📍 Warps: 14 locations</div>
				<div class="info-item">⚔️ Encounter Zones: 8×8 grid</div>
				<div class="info-item" id="cursorInfo">🖱️ Position: -,-</div>
				<div class="info-item" id="tileInfo">🎲 Tile: -</div>
				<div class="info-item" id="encounterInfo">⚔️ Encounters: -</div>
			</div>
		</div>

		<div class="map-container">
			<canvas id="canvas"></canvas>
		</div>
	</div>

	<script>
"""

	# Embed map data as JavaScript
	html += f"        const MAP_DATA = {json.dumps(tiles)};\n"
	html += f"        const MAP_WIDTH = {width};\n"
	html += f"        const MAP_HEIGHT = {height};\n"
	html += f"        const WARP_POINTS = {json.dumps(WARP_POINTS)};\n"
	html += f"        const ENCOUNTER_GRID = {json.dumps(ENCOUNTER_GRID)};\n"
	html += f"        const ENCOUNTER_NAMES = {json.dumps(ENCOUNTER_NAMES)};\n"

	html += """
		// Tile colors
		const TILE_COLORS = {
			0: [34, 177, 76],      // Grass
			1: [255, 217, 102],    // Desert
			2: [139, 90, 43],      // Hills
			3: [96, 96, 96],       // Mountain
			4: [0, 112, 221],      // Water
			5: [64, 64, 64],       // Rock Wall
			6: [0, 100, 0],        // Forest
			7: [128, 0, 128],      // Poison
			8: [192, 192, 192],    // Town
			9: [139, 69, 19],      // Tunnel
			10: [255, 215, 0],     // Castle
			11: [210, 180, 140],   // Bridge
			12: [255, 165, 0],     // Stairs
			13: [255, 0, 255],     // Unknown
			14: [255, 0, 255],     // Unknown
			15: [255, 0, 255]      // Unknown
		};

		const canvas = document.getElementById('canvas');
		const ctx = canvas.getContext('2d');

		let zoom = 4;
		let offsetX = 0;
		let offsetY = 0;
		let isDragging = false;
		let dragStartX = 0;
		let dragStartY = 0;
		let showGrid = true;
		let showWarps = true;
		let showEncounters = true;

		// Set canvas size
		function resizeCanvas() {
			const container = canvas.parentElement;
			canvas.width = Math.min(MAP_WIDTH * zoom, container.clientWidth - 40);
			canvas.height = Math.min(MAP_HEIGHT * zoom, container.clientHeight - 40);
			draw();
		}

		// Draw map
		function draw() {
			ctx.clearRect(0, 0, canvas.width, canvas.height);

			const startX = Math.floor(-offsetX / zoom);
			const startY = Math.floor(-offsetY / zoom);
			const endX = Math.min(MAP_WIDTH, startX + Math.ceil(canvas.width / zoom) + 1);
			const endY = Math.min(MAP_HEIGHT, startY + Math.ceil(canvas.height / zoom) + 1);

			// Draw tiles
			for (let y = Math.max(0, startY); y < endY; y++) {
				for (let x = Math.max(0, startX); x < endX; x++) {
					const tile = MAP_DATA[y][x];
					const color = TILE_COLORS[tile.type] || [255, 0, 255];

					ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
					ctx.fillRect(
						x * zoom + offsetX,
						y * zoom + offsetY,
						zoom,
						zoom
					);
				}
			}

			// Draw encounter zones
			if (showEncounters && zoom >= 4) {
				ctx.strokeStyle = 'rgba(255, 255, 0, 0.5)';
				ctx.lineWidth = 2;
				const gridSize = MAP_WIDTH / 8;

				for (let gy = 0; gy < 8; gy++) {
					for (let gx = 0; gx < 8; gx++) {
						const x1 = gx * gridSize * zoom + offsetX;
						const y1 = gy * gridSize * zoom + offsetY;
						const size = gridSize * zoom;

						ctx.strokeRect(x1, y1, size, size);

						if (zoom >= 8) {
							const encounterZone = ENCOUNTER_GRID[gy][gx];
							ctx.fillStyle = 'rgba(255, 255, 0, 0.8)';
							ctx.font = 'bold 12px monospace';
							ctx.fillText(encounterZone.toString(16).toUpperCase(), x1 + 5, y1 + 15);
						}
					}
				}
			}

			// Draw grid
			if (showGrid && zoom >= 8) {
				ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
				ctx.lineWidth = 1;

				for (let x = 0; x <= MAP_WIDTH; x += 8) {
					ctx.beginPath();
					ctx.moveTo(x * zoom + offsetX, offsetY);
					ctx.lineTo(x * zoom + offsetX, MAP_HEIGHT * zoom + offsetY);
					ctx.stroke();
				}

				for (let y = 0; y <= MAP_HEIGHT; y += 8) {
					ctx.beginPath();
					ctx.moveTo(offsetX, y * zoom + offsetY);
					ctx.lineTo(MAP_WIDTH * zoom + offsetX, y * zoom + offsetY);
					ctx.stroke();
				}
			}

			// Draw warp points
			if (showWarps) {
				WARP_POINTS.forEach(warp => {
					const x = warp.from_x * zoom + offsetX;
					const y = warp.from_y * zoom + offsetY;

					// Draw marker
					ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
					ctx.beginPath();
					ctx.arc(x + zoom/2, y + zoom/2, Math.max(3, zoom/2), 0, Math.PI * 2);
					ctx.fill();

					ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
					ctx.lineWidth = 2;
					ctx.stroke();

					// Draw label if zoomed in
					if (zoom >= 8) {
						ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
						ctx.fillRect(x - 40, y - 25, 80, 15);
						ctx.fillStyle = 'white';
						ctx.font = 'bold 10px monospace';
						ctx.textAlign = 'center';
						ctx.fillText(warp.name, x, y - 15);
						ctx.textAlign = 'left';
					}
				});
			}
		}

		// Mouse events
		canvas.addEventListener('mousedown', e => {
			isDragging = true;
			dragStartX = e.clientX - offsetX;
			dragStartY = e.clientY - offsetY;
		});

		canvas.addEventListener('mousemove', e => {
			if (isDragging) {
				offsetX = e.clientX - dragStartX;
				offsetY = e.clientY - dragStartY;
				draw();
			}

			// Update cursor info
			const rect = canvas.getBoundingClientRect();
			const mouseX = e.clientX - rect.left;
			const mouseY = e.clientY - rect.top;
			const tileX = Math.floor((mouseX - offsetX) / zoom);
			const tileY = Math.floor((mouseY - offsetY) / zoom);

			if (tileX >= 0 && tileX < MAP_WIDTH && tileY >= 0 && tileY < MAP_HEIGHT) {
				const tile = MAP_DATA[tileY][tileX];
				const gridX = Math.floor(tileX / 15);
				const gridY = Math.floor(tileY / 15);
				const encounterZone = ENCOUNTER_GRID[gridY] ? ENCOUNTER_GRID[gridY][gridX] : 0;
				const encounterName = ENCOUNTER_NAMES[encounterZone] || 'Unknown';

				document.getElementById('cursorInfo').textContent = `🖱️ Position: ${tileX},${tileY}`;
				document.getElementById('tileInfo').textContent = `🎲 Tile: ${tile.name}`;
				document.getElementById('encounterInfo').textContent = `⚔️ Encounters: ${encounterName}`;
			}
		});

		canvas.addEventListener('mouseup', () => { isDragging = false; });
		canvas.addEventListener('mouseleave', () => { isDragging = false; });

		// Zoom with mouse wheel
		canvas.addEventListener('wheel', e => {
			e.preventDefault();
			const delta = e.deltaY > 0 ? -1 : 1;
			zoom = Math.max(1, Math.min(16, zoom + delta));
			document.getElementById('zoomSlider').value = zoom;
			document.getElementById('zoomLevel').textContent = zoom + 'x';
			resizeCanvas();
		});

		// Zoom slider
		document.getElementById('zoomSlider').addEventListener('input', e => {
			zoom = parseInt(e.target.value);
			document.getElementById('zoomLevel').textContent = zoom + 'x';
			resizeCanvas();
		});

		// Checkboxes
		document.getElementById('showGrid').addEventListener('change', e => {
			showGrid = e.target.checked;
			draw();
		});

		document.getElementById('showWarps').addEventListener('change', e => {
			showWarps = e.target.checked;
			draw();
		});

		document.getElementById('showEncounters').addEventListener('change', e => {
			showEncounters = e.target.checked;
			draw();
		});

		// Functions
		function resetView() {
			zoom = 4;
			offsetX = 0;
			offsetY = 0;
			document.getElementById('zoomSlider').value = zoom;
			document.getElementById('zoomLevel').textContent = zoom + 'x';
			resizeCanvas();
		}

		function toggleFullscreen() {
			if (!document.fullscreenElement) {
				document.documentElement.requestFullscreen();
			} else {
				document.exitFullscreen();
			}
		}

		function jumpToLocation(x, y) {
			// Center view on location
			offsetX = canvas.width / 2 - x * zoom;
			offsetY = canvas.height / 2 - y * zoom;

			// Set good zoom level
			zoom = 8;
			document.getElementById('zoomSlider').value = zoom;
			document.getElementById('zoomLevel').textContent = zoom + 'x';

			resizeCanvas();
		}

		// Initialize
		window.addEventListener('resize', resizeCanvas);
		resizeCanvas();
	</script>
</body>
</html>
"""

	# Write HTML file
	output_path = Path(output_html_path)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write(html)

	print(f"✓ Generated interactive map: {output_path}")

def main():
	"""Generate interactive map HTML"""
	map_json = "extracted_assets/maps/overworld_map.json"
	output_html = "docs/asset_catalog/overworld_map_interactive.html"

	generate_interactive_map_html(map_json, output_html)

	print("\n✓ Interactive map viewer ready!")
	print(f"   Open {output_html} in your browser")

if __name__ == '__main__':
	main()
