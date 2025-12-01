package com.seattledevcamp.rainmaker.audio

import android.content.Context
import java.io.File
import java.io.FileOutputStream

object WavWriter {
    fun writeWav(context: Context, filename: String, sampleRate: Int, data: ShortArray): File {
        val outFile = File(context.filesDir, filename)
        val channels = 1
        val bitsPerSample = 16
        val byteRate = sampleRate * channels * bitsPerSample / 8
        val blockAlign = channels * bitsPerSample / 8
        val dataByteCount = data.size * 2
        val chunkSize = 36 + dataByteCount

        val header = ByteArray(44)

        // RIFF header
        header[0] = 'R'.code.toByte()
        header[1] = 'I'.code.toByte()
        header[2] = 'F'.code.toByte()
        header[3] = 'F'.code.toByte()
        writeLittleEndianInt(chunkSize, header, 4)
        header[8] = 'W'.code.toByte()
        header[9] = 'A'.code.toByte()
        header[10] = 'V'.code.toByte()
        header[11] = 'E'.code.toByte()

        // fmt subchunk
        header[12] = 'f'.code.toByte()
        header[13] = 'm'.code.toByte()
        header[14] = 't'.code.toByte()
        header[15] = ' '.code.toByte()
        writeLittleEndianInt(16, header, 16) // Subchunk1Size for PCM
        writeLittleEndianShort(1, header, 20) // AudioFormat PCM = 1
        writeLittleEndianShort(channels, header, 22)
        writeLittleEndianInt(sampleRate, header, 24)
        writeLittleEndianInt(byteRate, header, 28)
        writeLittleEndianShort(blockAlign, header, 32)
        writeLittleEndianShort(bitsPerSample, header, 34)

        // data subchunk
        header[36] = 'd'.code.toByte()
        header[37] = 'a'.code.toByte()
        header[38] = 't'.code.toByte()
        header[39] = 'a'.code.toByte()
        writeLittleEndianInt(dataByteCount, header, 40)

        FileOutputStream(outFile).use { fos ->
            fos.write(header)
            val buffer = ByteArray(2)
            for (s in data) {
                val v = s.toInt()
                buffer[0] = (v and 0xFF).toByte()
                buffer[1] = ((v shr 8) and 0xFF).toByte()
                fos.write(buffer)
            }
            fos.fd.sync()
        }
        return outFile
    }

    private fun writeLittleEndianInt(value: Int, array: ByteArray, offset: Int) {
        array[offset] = (value and 0xFF).toByte()
        array[offset + 1] = ((value shr 8) and 0xFF).toByte()
        array[offset + 2] = ((value shr 16) and 0xFF).toByte()
        array[offset + 3] = ((value shr 24) and 0xFF).toByte()
    }

    private fun writeLittleEndianShort(value: Int, array: ByteArray, offset: Int) {
        array[offset] = (value and 0xFF).toByte()
        array[offset + 1] = ((value shr 8) and 0xFF).toByte()
    }
}

