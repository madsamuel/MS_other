package com.seattledevcamp.rainmaker

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import java.io.File

enum class RainIntensity(val code: Int, val label: String) {
    LIGHT(0, "Light"), MEDIUM(1, "Medium"), HEAVY(2, "Heavy")
}

enum class Screen {
    GENERATOR, RECORDINGS
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val vm: GeneratorViewModel = viewModel<GeneratorViewModel>(factory = GeneratorViewModel.Factory(application))
                val status by vm.status.collectAsState(initial = "idle")
                val recordings by vm.recordings.collectAsState(initial = emptyList())
                val currentPlaying by vm.currentPlaying.collectAsState(initial = null)
                val isPlayingGlobal by vm.isPlaying.collectAsState(initial = false)

                // Persist the current screen across rotation by saving the enum ordinal.
                var currentScreenOrdinal by rememberSaveable { mutableStateOf(Screen.GENERATOR.ordinal) }

                // No intensity selected by default; Reset should restore this 'no selection' state.
                var selectedIntensity by remember { mutableStateOf<RainIntensity?>(null) }
                val modifiers = remember {
                    mutableStateMapOf(
                        "sea" to false,
                        "cliffs" to false,
                        "forest" to false,
                        "river" to false,
                        "city" to false,
                        "countryside" to false,
                        "cafe" to false
                    )
                }
                var durationSec by remember { mutableStateOf(30f) }

                // Auto-navigate to recordings when generation completes with saved:path
                LaunchedEffect(status) {
                    if (status.startsWith("saved:")) {
                        currentScreenOrdinal = Screen.RECORDINGS.ordinal
                        vm.refreshList()
                    }
                }

                Scaffold(
                    topBar = {
                        AppTopBar(
                            currentScreen = Screen.values()[currentScreenOrdinal],
                            onOpenRecordings = { currentScreenOrdinal = Screen.RECORDINGS.ordinal },
                            onBack = { currentScreenOrdinal = Screen.GENERATOR.ordinal }
                        )
                    },
                    content = { innerPadding ->
                        Box(modifier = Modifier.padding(innerPadding).fillMaxSize()) {
                            when (Screen.values()[currentScreenOrdinal]) {
                                Screen.GENERATOR -> GeneratorContent(
                                    selectedIntensity = selectedIntensity,
                                    onSelectIntensity = { selectedIntensity = it },
                                    modifiers = modifiers,
                                    durationSec = durationSec,
                                    onDurationChange = { durationSec = it },
                                    onGenerate = {
                                        val mask = modifiers.entries.fold(0) { acc, e -> if (e.value) acc or modifierMask(e.key) else acc }
                                        val seed = kotlin.random.Random.nextLong()
                                        val filename = "rain_${System.currentTimeMillis()}_${kotlin.math.abs(seed)}.wav"
                                        // If user hasn't picked an intensity, fall back to MEDIUM for generation
                                        val intensityCode = (selectedIntensity ?: RainIntensity.MEDIUM).code
                                        vm.generateRainFile(durationSec.toInt(), intensityCode, mask, filename, seed)
                                    },
                                    status = status,
                                    onRefresh = {
                                        // Reset UI to initial state: no intensity selected, clear modifiers, restore default duration
                                        selectedIntensity = null
                                        modifiers.keys.forEach { modifiers[it] = false }
                                        durationSec = 30f
                                        // also refresh recordings list in case caller expects it
                                        vm.refreshList()
                                    }
                                )
                                Screen.RECORDINGS -> RecordingsContent(
                                    recordings = recordings,
                                    currentPlaying = currentPlaying,
                                    isPlayingGlobal = isPlayingGlobal,
                                    onPlay = { vm.togglePlay(it) },
                                    onDelete = { vm.deleteFile(it) },
                                    onRefresh = { vm.refreshList() },
                                    onRename = { file, newName ->
                                        val trimmed = newName.trim()
                                        if (trimmed.isNotEmpty()) {
                                            val safeName = if (trimmed.endsWith(".wav", ignoreCase = true)) trimmed else "$trimmed.wav"
                                            val dir = file.parentFile
                                            if (dir != null) {
                                                val target = File(dir, safeName)
                                                when {
                                                    target.exists() -> vm.updateStatus("error: rename target exists")
                                                    file.renameTo(target) -> {
                                                        vm.updateStatus("renamed:${target.name}")
                                                    }
                                                    else -> {
                                                        vm.updateStatus("error: rename failed")
                                                    }
                                                }
                                            }
                                        }
                                        vm.refreshList()
                                    }
                                )
                            }
                        }
                    }
                )
            }
        }
    }

    private fun modifierMask(key: String): Int {
        return when (key) {
            "sea" -> 1 shl 0
            "cliffs" -> 1 shl 1
            "forest" -> 1 shl 2
            "river" -> 1 shl 3
            "city" -> 1 shl 4
            "countryside" -> 1 shl 5
            "cafe" -> 1 shl 6
            else -> 0
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun GeneratorContent(
    selectedIntensity: RainIntensity?,
    onSelectIntensity: (RainIntensity) -> Unit,
    modifiers: MutableMap<String, Boolean>,
    durationSec: Float,
    onDurationChange: (Float) -> Unit,
    onGenerate: () -> Unit,
    status: String,
    onRefresh: () -> Unit
) {
    Column(modifier = Modifier.padding(16.dp).verticalScroll(rememberScrollState())) {
        Spacer(Modifier.height(8.dp))

        Text("Intensity")
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf(RainIntensity.LIGHT, RainIntensity.MEDIUM, RainIntensity.HEAVY).forEach { r ->
                val isSelected = r == selectedIntensity
                Button(
                    onClick = { onSelectIntensity(r) },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.secondaryContainer,
                        contentColor = if (isSelected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSecondary
                    )
                ) {
                    Text(r.label)
                }
            }
        }

        Spacer(Modifier.height(12.dp))
        Text("Modifiers (environment)")
        FlowRow(modifiers.keys.toList()) { key ->
            val checked = modifiers[key] ?: false
            FilterChip(selected = checked, onClick = { modifiers[key] = !checked }, label = { Text(key) })
        }

        Spacer(Modifier.height(12.dp))
        Text("Duration: ${durationSec.toInt()}s")
        Slider(value = durationSec, onValueChange = onDurationChange, valueRange = 10f..3000f)

        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onGenerate) { Text("Generate") }
            Button(onClick = onRefresh) { Text("Reset") }
        }

        Spacer(Modifier.height(8.dp))
        Text("Status: $status")
    }
}

@Composable
private fun RecordingsContent(
    recordings: List<File>,
    currentPlaying: String?,
    isPlayingGlobal: Boolean,
    onPlay: (File) -> Unit,
    onDelete: (File) -> Unit,
    onRefresh: () -> Unit,
    onRename: (File, String) -> Unit
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text("Recordings", style = MaterialTheme.typography.titleMedium)
            Button(onClick = onRefresh) { Text("Reset") }
        }
        Spacer(Modifier.height(8.dp))
        LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            items(recordings) { f ->
                val playingForThis = (currentPlaying == f.absolutePath) && isPlayingGlobal
                RecordingRow(
                    file = f,
                    isPlaying = playingForThis,
                    onTogglePlay = { onPlay(f) },
                    onDelete = { onDelete(f) },
                    onRename = { newName -> onRename(f, newName) }
                )
            }
        }
    }
}

@Composable
private fun FlowRow(keys: List<String>, content: @Composable (String) -> Unit) {
    Column {
        val maxPerRow = 3
        keys.chunked(maxPerRow).forEach { chunk ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                chunk.forEach { key -> content(key) }
            }
            Spacer(Modifier.height(8.dp))
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun RecordingRow(
    file: File,
    isPlaying: Boolean,
    onTogglePlay: () -> Unit,
    onDelete: () -> Unit,
    onRename: (String) -> Unit
) {
    var showRenameDialog by remember { mutableStateOf(false) }
    var newName by remember { mutableStateOf(file.name) }

    Card(modifier = Modifier
        .fillMaxWidth()
        .padding(vertical = 4.dp)) {
        Row(
            modifier = Modifier
                .padding(12.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Constrain the text column so action buttons keep space on narrow screens.
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = file.name,
                    style = MaterialTheme.typography.bodyLarge,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = "${file.length() / 1024} KB",
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
            Row {
                if (isPlaying) {
                    TextButton(onClick = onTogglePlay) { Text("Pause") }
                } else {
                    IconButton(onClick = onTogglePlay) { Icon(Icons.Default.PlayArrow, contentDescription = "Play") }
                }
                IconButton(onClick = { showRenameDialog = true }) {
                    Icon(Icons.Default.Edit, contentDescription = "Rename")
                }
                IconButton(onClick = onDelete) { Icon(Icons.Default.Delete, contentDescription = "Delete") }
            }
        }
    }

    if (showRenameDialog) {
        AlertDialog(
            onDismissRequest = { showRenameDialog = false },
            title = { Text("Rename recording") },
            text = {
                Column {
                    Text("Enter a new name (without extension). .wav will be added if missing.")
                    Spacer(Modifier.height(8.dp))
                    TextField(value = newName, onValueChange = { newName = it }, singleLine = true)
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    onRename(newName)
                    showRenameDialog = false
                }) {
                    Text("OK")
                }
            },
            dismissButton = {
                TextButton(onClick = { showRenameDialog = false }) { Text("Cancel") }
            }
        )
    }
}

@Composable
private fun AppTopBar(currentScreen: Screen, onOpenRecordings: () -> Unit, onBack: () -> Unit) {
    Surface(tonalElevation = 4.dp, modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                if (currentScreen == Screen.GENERATOR) "Rain Mix Generator" else "Recordings",
                style = MaterialTheme.typography.titleLarge
            )
            if (currentScreen == Screen.GENERATOR) {
                TextButton(onClick = onOpenRecordings) { Text("Recordings") }
            } else {
                TextButton(onClick = onBack) { Text("Back") }
            }
        }
    }
}
