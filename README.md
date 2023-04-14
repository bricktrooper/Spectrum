# Spectrum

Spectrum is a 10-band stereo graphic equalizer circuit.  It uses active band pass filters in a multiple feedback configuration.  Each band can be individually amplified or attenuated using linear potentiometers.  The circuit requires an external power source of at least 5 V at 250 mA.

## Background

### Graphic Equalizers

A graphic equalizer is a piece of audio equipment that isolates different ranges of frequencies from an audio signal.  These ranges can then be individually amplified (boosted) or attenuated (cut).  The modified signals are mixed back together into a single audio signal which appears at the output.  The resulting signal is the same audio but with each frequency range adjusted with a desired gain.

### Stereo Sound

The most basic form of electrical audio signals is "mono".  This is a single audio signal that plays through all the speakers.  "Stereo" uses two separate audio signals that differ slightly but can be used to give the perception of spatial audio.  Typically, the signals are used to drive separate "left" and "right" speakers.  A graphic equalizer only operates on a single mono signal.  Spectrum effectively uses two identical mono circuits to modify both channels of stereo audio.  The resulting output can be played through stereo headphones.  The circuit must be powered by an external wall adapter or any other 5 V source that can supply approximately 250 mA of current.

## Circuit Design

### Power Supply

Spectrum uses a 5 V power supply that is regulated by an L7805 LDO.  Traditionally, operational amplifiers use a bipolar supply of +VDD and -VDD, with the ground point of the signal being 0 V.  This is not possible with a single supply.  Therefore, Spectrum raises the ground point to a virtual ground of (VDD / 2), or 2.5 V.  The op amps are supplied by 5 V and sink to 0 V (GND).  This provides 2.5 V of signal swing, which is enough for driving headphones to a considerable volume.  To drive large speakers, a separate amplifier should be used.  Capacitive coupling is used to inject an AC audio signal into a 2.5 V bias and decouple the bias at the output headphone jack.

### Preamplifier

The preamplifier's job is to drive the rest of the circuit, effectively isolating the input resistance of the circuit from the audio source.  This is important because headphone jack outputs cannot drive very high impedances.  The preamplifer is also capable of amplifying or attenuating the input signal.  Amplification may be required if the input source is too quiet, while attenuation can be used to reduce distortion in the output signal.  The input to the preamplifier is further isolated using a 1:1 audio transformer.  This prevents the ground of the circuit from creating a ground loop through the audio cable, which creates an undesirable humming noise due to the oscillation of the AC mains voltage.  The preamplifier is implemented as a simple inverting amplifier.  A capacitor is used at the input to strip out any existing DC voltage and the output signal is re-biased at the virtual ground point.  A potentiometer is used in the feedback resistance to amplify or attenuate the signal linearly.

### Band Pass Filters

The core circuit of a graphic equalizer is the band pass filter, which isolates a range of frequencies.  Different resistor and capacitor values are used to achieve different cutoff frequencies over the bass, mid, and treble ranges.  Spectrum uses 10 filters for each audio channel.  The centre frequencies are chosen based on standard octaves:

- 31.5 Hz
- 63 Hz
- 125 Hz
- 250 Hz
- 500 Hz
- 1 kHz
- 2 kHz
- 4 kHz
- 8 kHz
- 16 kHz

These are active filters that used op amps in the multiple-feedback configuration, which allows the cutoff frequency to be changed without affecting the gain of the centre frequency.  The gain of all the filters have been adjusted so that the entire audio range has a flat gain response when the filter outputs are mixed back together.  Each individual filter has a DC gain of 1 V/V, with the exception of 31.5 Hz and 16 kHz, which have a gain of 1.6 V/V.  A quality factor of Q = 1.7 is used for all filters.  The component selection is as follows:

```
-------------------------------------------------------------------------------------------------------------------
| BAND    | ERROR      | C          | R1         | R2         | R3         | f          | Q          | A          |
-------------------------------------------------------------------------------------------------------------------
| 31.5 Hz | 0.816      | 0.33 uF    | 16 K       | 51 K       | 6.2 K      | 31.948 Hz  | 1.689      | 1.594 V/V  |
| 63 Hz   | 0.745      | 0.56 uF    | 7.5 K      | 15 K       | 1.6 K      | 63.902 Hz  | 1.686      | 1.000 V/V  |
| 125 Hz  | 0.709      | 0.22 uF    | 10 K       | 20 K       | 2 K        | 125.302 Hz | 1.732      | 1.000 V/V  |
| 250 Hz  | 0.709      | 0.1 uF     | 11 K       | 22 K       | 2.2 K      | 250.604 Hz | 1.732      | 1.000 V/V  |
| 500 Hz  | 1.204      | 0.1 uF     | 5.6 K      | 11 K       | 1.1 K      | 500.462 Hz | 1.729      | 0.982 V/V  |
| 1 kHz   | 1.328      | 0.18 uF    | 1.5 K      | 3 K        | 0.3 K      | 1.021 kHz  | 1.732      | 1.000 V/V  |
| 2 kHz   | 0.467      | 0.18 uF    | 0.75 K     | 1.5 K      | 0.16 K     | 1.988 kHz  | 1.686      | 1.000 V/V  |
| 4 kHz   | 1.078      | 0.068 uF   | 1 K        | 2 K        | 0.2 K      | 4.054 kHz  | 1.732      | 1.000 V/V  |
| 8 kHz   | 0.812      | 0.033 uF   | 1 K        | 2 K        | 0.22 K     | 8.031 kHz  | 1.665      | 1.000 V/V  |
| 16 kHz  | 0.916      | 0.022 uF   | 0.47 K     | 1.5 K      | 0.18 K     | 16.373 kHz | 1.697      | 1.596 V/V  |
-------------------------------------------------------------------------------------------------------------------
```

### Band Amplifiers

Each band pass filter is followed by an inverting amplifier, which has adjustable gain via a potentiometer in the feedback path.  This allows the user to individually boost or cut different frequency ranges.  At the potentiometer neutral point, the gain of the band amplifier is 0.5 V/V, meaning that each band can be attenuated down to 0 V/V or boosted up to 1 V/V, which is the gain of the band pass filters.  Any further amplification must be provided from the audio source and the preamplifier.  Due to band overlap, the actual realized gain is slightly higher or lower than in theory.  This is a tradeoff between selectivity and gain accuracy.

### Mixer

The mixer is a summing amplifier that re-combines all the band signals back into a single audio signal.  It has a fixed gain of 5 V/V, and the output signal can directly drive low-impedance headphones.  The output signal runs through a large capacitor to cut out the virtual ground DC bias to avoid damaging the headphone speaker coils.  This turns the signal into an AC waveform with a GND as the reference point.

## Schematic

![Schematic](images/schematic.png)

## Circuit Board

### Top
![Top](images/board_top.png)

### Bottom
![Bottom](images/board_bottom.png)

### Assembled
![Assembled](images/board_assembled.png)

## Revisions

- A 470R resistor was added to the audio output to mitigate the amplified hissing noise.  The side effect of this is reduced gain from the preamp and increased distortion in the output signal.

