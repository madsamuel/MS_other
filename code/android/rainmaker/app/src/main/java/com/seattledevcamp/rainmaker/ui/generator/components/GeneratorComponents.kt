package com.seattledevcamp.rainmaker.ui.generator.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Snackbar
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.seattledevcamp.rainmaker.data.model.RainIntensity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

@Composable
fun ModifierChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    FilterChip(
        modifier = modifier,
        selected = selected,
        onClick = onClick,
        label = { Text(label) },
        shape = CircleShape
    )
}

@Composable
fun RainIntensitySelector(
    selected: RainIntensity,
    onSelect: (RainIntensity) -> Unit
) {
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        RainIntensity.entries.forEach { intensity ->
            val title = intensity.name.lowercase().replaceFirstChar(Char::uppercase)
            FilterChip(
                selected = intensity == selected,
                onClick = { onSelect(intensity) },
                label = { Text(title) },
                shape = CircleShape
            )
        }
    }
}

@Composable
fun SnackbarHost(
    message: String,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(message) {
        snackbarHostState.currentSnackbarData?.dismiss()
        snackbarHostState.showSnackbar(message)
        onDismiss()
    }
    androidx.compose.material3.SnackbarHost(
        modifier = modifier.padding(horizontal = 8.dp),
        hostState = snackbarHostState,
        snackbar = { data -> Snackbar { Text(data.visuals.message) } }
    )
}

