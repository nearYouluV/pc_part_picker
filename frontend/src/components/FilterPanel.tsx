import type { ReactNode } from 'react';

interface Props {
    category: string;
    filters: Record<string, string | number | boolean | null | undefined>;
    setFilters: (filters: Record<string, string | number | boolean | null | undefined>) => void;
    onClose?: () => void;
}

function Field({ label, children, wide = false }: { label: string; children: ReactNode; wide?: boolean }) {
    return (
        <label className={wide ? 'block md:col-span-2' : 'block'}>
            <span className="text-sm text-[color:var(--text-soft)]">{label}</span>
            <div className="mt-2">{children}</div>
        </label>
    );
}

function inputValue(value: string | number | boolean | null | undefined) {
    if (typeof value === 'string' || typeof value === 'number') {
        return value;
    }

    return '';
}

export default function FilterPanel({ category, filters, setFilters, onClose }: Props) {
    const update = (patch: Record<string, string | number | boolean | null | undefined>) => {
        setFilters({ ...filters, ...patch });
    };

    const reset = () => {
        setFilters({ compatible_only: true, min_price: '', max_price: '' });
    };

    return (
        <div className="soft-card border border-[var(--border-strong)] p-4 rounded-2xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Field label="Compatible only">
                    <button
                        type="button"
                        onClick={() => update({ compatible_only: !filters.compatible_only })}
                        className={`min-h-11 px-4 rounded-xl border text-sm font-semibold inline-flex items-center gap-2 transition-all duration-150 ${filters.compatible_only
                            ? 'bg-[color:var(--primary)] text-white border-transparent'
                            : 'bg-[var(--surface)] border-[var(--border-strong)] text-[color:var(--text-main)]'
                            }`}
                    >
                        {filters.compatible_only ? 'On' : 'Off'}
                    </button>
                </Field>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Field label="Min price">
                        <input type="number" min={0} value={inputValue(filters.min_price)} onChange={(e) => update({ min_price: e.target.value })} className="input-premium" />
                    </Field>
                    <Field label="Max price">
                        <input type="number" min={0} value={inputValue(filters.max_price)} onChange={(e) => update({ max_price: e.target.value })} className="input-premium" />
                    </Field>
                </div>
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {category === 'cpu' && (
                    <>
                        <Field label="Cores min">
                            <input type="number" min={0} value={inputValue(filters.cores_min)} onChange={(e) => update({ cores_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Cores max">
                            <input type="number" min={0} value={inputValue(filters.cores_max)} onChange={(e) => update({ cores_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Base clock min (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.base_clock_min)} onChange={(e) => update({ base_clock_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Base clock max (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.base_clock_max)} onChange={(e) => update({ base_clock_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Boost clock min (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.boost_clock_min)} onChange={(e) => update({ boost_clock_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Boost clock max (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.boost_clock_max)} onChange={(e) => update({ boost_clock_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="TDP min (W)">
                            <input type="number" min={0} value={inputValue(filters.tdp_min)} onChange={(e) => update({ tdp_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="TDP max (W)">
                            <input type="number" min={0} value={inputValue(filters.tdp_max)} onChange={(e) => update({ tdp_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="L3 cache range" wide>
                            <select value={inputValue(filters.l3_cache_band)} onChange={(e) => update({ l3_cache_band: e.target.value })} className="select-premium w-full">
                                <option value="">Any</option>
                                <option value="gt65">More than 65 MB</option>
                                <option value="41_64">41 - 64 MB</option>
                                <option value="25_40">25 - 40 MB</option>
                                <option value="10_24">10 - 24 MB</option>
                                <option value="lt10">Less than 10 MB</option>
                            </select>
                        </Field>
                    </>
                )}

                {category === 'gpu' && (
                    <>
                        <Field label="VRAM min (GB)">
                            <input type="number" min={0} value={inputValue(filters.vram_min)} onChange={(e) => update({ vram_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="VRAM max (GB)">
                            <input type="number" min={0} value={inputValue(filters.vram_max)} onChange={(e) => update({ vram_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Frequency min (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.frequency_min)} onChange={(e) => update({ frequency_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Frequency max (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.frequency_max)} onChange={(e) => update({ frequency_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Performance min">
                            <input type="number" min={0} value={inputValue(filters.performance_min)} onChange={(e) => update({ performance_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Performance max">
                            <input type="number" min={0} value={inputValue(filters.performance_max)} onChange={(e) => update({ performance_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Recommended PSU min (W)">
                            <input type="number" min={0} value={inputValue(filters.recommended_power_supply_min)} onChange={(e) => update({ recommended_power_supply_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Recommended PSU max (W)">
                            <input type="number" min={0} value={inputValue(filters.recommended_power_supply_max)} onChange={(e) => update({ recommended_power_supply_max: e.target.value })} className="input-premium" />
                        </Field>
                    </>
                )}

                {category === 'motherboard' && (
                    <>
                        <Field label="Socket">
                            <input type="text" value={inputValue(filters.socket)} onChange={(e) => update({ socket: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Chipset">
                            <input type="text" value={inputValue(filters.chipset)} onChange={(e) => update({ chipset: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="RAM type">
                            <select value={inputValue(filters.ram_type)} onChange={(e) => update({ ram_type: e.target.value })} className="select-premium w-full">
                                <option value="">Any</option>
                                <option value="ddr4">DDR4</option>
                                <option value="ddr5">DDR5</option>
                            </select>
                        </Field>
                        <Field label="Max RAM min (GB)">
                            <input type="number" min={0} value={inputValue(filters.max_ram_min)} onChange={(e) => update({ max_ram_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Max RAM max (GB)">
                            <input type="number" min={0} value={inputValue(filters.max_ram_max)} onChange={(e) => update({ max_ram_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Memory slots min">
                            <input type="number" min={0} value={inputValue(filters.memory_slots_min)} onChange={(e) => update({ memory_slots_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Memory slots max">
                            <input type="number" min={0} value={inputValue(filters.memory_slots_max)} onChange={(e) => update({ memory_slots_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="M.2 slots min">
                            <input type="number" min={0} value={inputValue(filters.m2_slots_min)} onChange={(e) => update({ m2_slots_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="M.2 slots max">
                            <input type="number" min={0} value={inputValue(filters.m2_slots_max)} onChange={(e) => update({ m2_slots_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="SATA ports min">
                            <input type="number" min={0} value={inputValue(filters.sata_ports_min)} onChange={(e) => update({ sata_ports_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="SATA ports max">
                            <input type="number" min={0} value={inputValue(filters.sata_ports_max)} onChange={(e) => update({ sata_ports_max: e.target.value })} className="input-premium" />
                        </Field>
                    </>
                )}

                {category === 'ram' && (
                    <>
                        <Field label="Capacity min (GB)">
                            <input type="number" min={0} value={inputValue(filters.capacity_min)} onChange={(e) => update({ capacity_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Capacity max (GB)">
                            <input type="number" min={0} value={inputValue(filters.capacity_max)} onChange={(e) => update({ capacity_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Frequency min (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.frequency_min)} onChange={(e) => update({ frequency_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Frequency max (GHz)">
                            <input type="number" step="0.1" min={0} value={inputValue(filters.frequency_max)} onChange={(e) => update({ frequency_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="CAS latency min">
                            <input type="number" min={0} value={inputValue(filters.cas_latency_min)} onChange={(e) => update({ cas_latency_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="CAS latency max">
                            <input type="number" min={0} value={inputValue(filters.cas_latency_max)} onChange={(e) => update({ cas_latency_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Modules count min">
                            <input type="number" min={0} value={inputValue(filters.modules_count_min)} onChange={(e) => update({ modules_count_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Modules count max">
                            <input type="number" min={0} value={inputValue(filters.modules_count_max)} onChange={(e) => update({ modules_count_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="RAM type">
                            <input type="text" value={inputValue(filters.ram_type)} onChange={(e) => update({ ram_type: e.target.value })} className="input-premium" />
                        </Field>
                    </>
                )}

                {category === 'psu' && (
                    <>
                        <Field label="Power min (W)">
                            <input type="number" min={0} value={inputValue(filters.power_min)} onChange={(e) => update({ power_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Power max (W)">
                            <input type="number" min={0} value={inputValue(filters.power_max)} onChange={(e) => update({ power_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Certification">
                            <input type="text" value={inputValue(filters.certification)} onChange={(e) => update({ certification: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Modular only">
                            <button
                                type="button"
                                onClick={() => update({ modularity: filters.modularity === true ? null : true })}
                                className="min-h-11 px-4 rounded-xl border text-sm font-semibold inline-flex items-center gap-2 bg-[var(--surface)] border-[var(--border-strong)] text-[color:var(--text-main)]"
                            >
                                {filters.modularity === true ? 'On' : 'Off'}
                            </button>
                        </Field>
                    </>
                )}

                {category === 'storage' && (
                    <>
                        <Field label="Capacity min (GB)">
                            <input type="number" min={0} value={inputValue(filters.capacity_min)} onChange={(e) => update({ capacity_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Capacity max (GB)">
                            <input type="number" min={0} value={inputValue(filters.capacity_max)} onChange={(e) => update({ capacity_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Read speed min (MB/s)">
                            <input type="number" min={0} value={inputValue(filters.read_speed_min)} onChange={(e) => update({ read_speed_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Read speed max (MB/s)">
                            <input type="number" min={0} value={inputValue(filters.read_speed_max)} onChange={(e) => update({ read_speed_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Write speed min (MB/s)">
                            <input type="number" min={0} value={inputValue(filters.write_speed_min)} onChange={(e) => update({ write_speed_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Write speed max (MB/s)">
                            <input type="number" min={0} value={inputValue(filters.write_speed_max)} onChange={(e) => update({ write_speed_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="RPM min">
                            <input type="number" min={0} value={inputValue(filters.rpm_min)} onChange={(e) => update({ rpm_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="RPM max">
                            <input type="number" min={0} value={inputValue(filters.rpm_max)} onChange={(e) => update({ rpm_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Interface">
                            <input type="text" value={inputValue(filters.interface)} onChange={(e) => update({ interface: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Form factor">
                            <input type="text" value={inputValue(filters.form_factor)} onChange={(e) => update({ form_factor: e.target.value })} className="input-premium" />
                        </Field>
                    </>
                )}

                {category === 'cooler' && (
                    <>
                        <Field label="TDP support min (W)">
                            <input type="number" min={0} value={inputValue(filters.tdp_support_min)} onChange={(e) => update({ tdp_support_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="TDP support max (W)">
                            <input type="number" min={0} value={inputValue(filters.tdp_support_max)} onChange={(e) => update({ tdp_support_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Noise level min">
                            <input type="number" min={0} value={inputValue(filters.noise_level_min)} onChange={(e) => update({ noise_level_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Noise level max">
                            <input type="number" min={0} value={inputValue(filters.noise_level_max)} onChange={(e) => update({ noise_level_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Fan count min">
                            <input type="number" min={0} value={inputValue(filters.fan_count_min)} onChange={(e) => update({ fan_count_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Fan count max">
                            <input type="number" min={0} value={inputValue(filters.fan_count_max)} onChange={(e) => update({ fan_count_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Height min (mm)">
                            <input type="number" min={0} value={inputValue(filters.height_min)} onChange={(e) => update({ height_min: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Height max (mm)">
                            <input type="number" min={0} value={inputValue(filters.height_max)} onChange={(e) => update({ height_max: e.target.value })} className="input-premium" />
                        </Field>
                        <Field label="Cooling type">
                            <select value={inputValue(filters.cooling_type)} onChange={(e) => update({ cooling_type: e.target.value })} className="select-premium w-full">
                                <option value="">Any</option>
                                <option value="AIR">Air</option>
                                <option value="LIQUID">Water</option>
                            </select>
                        </Field>
                        <Field label="Socket support">
                            <input type="text" value={inputValue(filters.socket_support)} onChange={(e) => update({ socket_support: e.target.value })} className="input-premium" />
                        </Field>
                    </>
                )}
            </div>

            <div className="mt-4 flex items-center gap-3 justify-end">
                <button type="button" onClick={reset} className="btn-ghost">Reset</button>
                <button type="button" onClick={onClose} className="btn-secondary">Apply</button>
            </div>
        </div>
    );
}
