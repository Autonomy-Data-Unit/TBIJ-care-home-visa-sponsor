<script lang="ts">
    import {
        createTable,
        Render,
        Subscribe,
        createRender,
    } from "svelte-headless-table";
    import {
        addPagination,
        addSortBy,
        addTableFilter,
    } from "svelte-headless-table/plugins";
    import { readable } from "svelte/store";
    import ArrowUpDown from "lucide-svelte/icons/arrow-up-down";
    import * as Table from "$lib/components/ui/table";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";

    import * as Command from "$lib/components/ui/command";
    import * as Popover from "$lib/components/ui/popover";
    import { cn } from "$lib/utils.js";
    import { tick } from "svelte";
    import Check from "lucide-svelte/icons/check";
    import ChevronsUpDown from "lucide-svelte/icons/chevrons-up-down";
    import { writable } from "svelte/store";

    export let data: any[] = [];
    let dataStore = writable(data);
    export let place_merc_lookup = {};

    const table = createTable(dataStore, {
        page: addPagination({
            initialPageSize: 12,
        }),
        sort: addSortBy({
            initialSortKeys: [
                { id: "distance", order: "asc" }, // Replace 'name' with the accessor of the column you want to sort by default
            ],
        }),
        filter: addTableFilter({
            fn: ({ filterValue, value }) =>
                value.toLowerCase().includes(filterValue.toLowerCase()),
        }),
    });

    const columns = table.createColumns([
        table.column({
            accessor: "Organisation Name",
            header: "Organisation Name",
            plugins: {
                sort: {
                    disable: true,
                },
                filter: addTableFilter({
                    fn: ({ filterValue, value }) =>
                        value.toLowerCase().includes(filterValue.toLowerCase()),
                }),
            },
        }),
        table.column({
            accessor: "Town/City",
            header: "Town/City",
            plugins: {
                sort: {
                    disable: true,
                },
                filter: {
                    exclude: true,
                },
            },
        }),
        table.column({
            accessor: "County",
            header: "County",
            plugins: {
                sort: {
                    disable: true,
                },
                filter: {
                    exclude: true,
                },
            },
        }),
        table.column({
            accessor: "distance",
            header: "Approximate distance",
            plugins: {
                filter: {
                    exclude: true,
                },
            },
        }),
    ]);

    const { headerRows, pageRows, tableAttrs, tableBodyAttrs, pluginStates } =
        table.createViewModel(columns);

    const { pageIndex, pageCount, pageSize, hasNextPage, hasPreviousPage } =
        pluginStates.page;
    const { filterValue } = pluginStates.filter;

    /*** Location ComboBox ***/

    function capitalize(str: string) {
        return str
            .split(" ")
            .map(
                (word) =>
                    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase(),
            )
            .join(" ");
    }

    const places = Object.keys(place_merc_lookup).map((place) => ({
        value: place,
        label: capitalize(place),
        merc_x: place_merc_lookup[place][0],
        merc_y: place_merc_lookup[place][1],
    }));

    let open = false;
    let value = "";

    $: selectedValue =
        places.find((f) => f.value === value)?.label ?? "Select location";

    // We want to refocus the trigger button when the user selects
    // an item from the list so users can continue navigating the
    // rest of the form with the keyboard.
    function closeAndFocusTrigger(triggerId: string) {
        open = false;
        tick().then(() => {
            document.getElementById(triggerId)?.focus();
        });
    }

    let placeFilter: string;
    $: filteredPlaces = places
        .filter((place) => place.value.includes(placeFilter))
        .slice(0, 15);

    // Calculate the distances
    $: {
        if (selectedValue.toLowerCase() in place_merc_lookup) {
            const selectedPlace =
                place_merc_lookup[selectedValue.toLowerCase()];
            data.forEach((e) => {
                e.distance = Math.sqrt(
                    Math.pow(selectedPlace[0] - e.merc_x, 2) +
                        Math.pow(selectedPlace[1] - e.merc_y, 2),
                );
                e.distance /= 1000;
            });
        }
        data = [...data];
        dataStore.set(data);
    }

    // Postcodes

    let search_postcode = "";

    function valid_postcode(postcode) {
        postcode = postcode.replace(/\s/g, "");
        var regex = /^[A-Z]{1,2}[0-9]{1,2} ?[0-9][A-Z]{2}$/i;
        return regex.test(postcode);
    }

    async function getPostcodeInfo(postcode) {
        // Get the postcode from the input field
        postcode = postcode.trim();

        // API URL with the entered postcode
        var url =
            "https://api.postcodes.io/postcodes/" +
            encodeURIComponent(postcode);

        try {
            // Fetch API call to the postcode API
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();

            // Handling the response data
            if (data.status === 200 && data.result) {
                // Return the formatted postcode data
                return JSON.stringify(data.result, null, 2);
            } else {
                // Handle no data found or other errors
                return "Postcode not found or error in API call.";
            }
        } catch (error) {
            // Handle network errors
            console.error("Error fetching data: ", error);
            return "Failed to fetch data.";
        }
    }

    async function fetchPostcodeInfo() {
        if (valid_postcode(search_postcode)) {
            const result = await getPostcodeInfo(search_postcode);
            return result;
        }
    }

    function lat_lng_to_mercator(lat, lng) {
        const r_major = 6378137.0;
        const x = r_major * Math.radians(lng);
        const scale = x / lng;
        const y =
            (180.0 / Math.PI) *
            Math.log(
                Math.tan(Math.PI / 4.0 + (lat * (Math.PI / 180.0)) / 2.0),
            ) *
            scale;
        return [x, y];
    }

    function formatDistanceAsStr(distance) {
        if (distance < 1) {
            return "Less than 1km";
        } else if (distance < 5) {
            return "Less than 5km";
        } else if (distance < 10) {
            return "5-10km";
        } else if (distance < 50) {
            return "10-50km";
        } else if (distance < 100) {
            return "50-100km";
        } else if (distance < 500) {
            return "100-500km";
        } else {
            return "500km or more";
        }
    }

    // JavaScript doesn't have a built-in function to convert degrees to radians
    Math.radians = function (degrees) {
        return (degrees * Math.PI) / 180;
    };

    const postcode_to_merc_lookup = {};

    function update_distances(sx, sy) {
        data.forEach((e) => {
            e.distance = Math.sqrt(
                Math.pow(sx - e.merc_x, 2) + Math.pow(sy - e.merc_y, 2),
            );
            e.distance /= 1000;
        });

        data = [...data];
        dataStore.set(data);
    }
    function reset_distances() {
        data.forEach((e) => {
            e.distance = null;
        });

        data = [...data];
        dataStore.set(data);
    }

    $: {
        if (valid_postcode(search_postcode)) {
            if (!(search_postcode in postcode_to_merc_lookup)) {
                fetchPostcodeInfo().then((result) => {
                    result = JSON.parse(result);
                    const merc = lat_lng_to_mercator(
                        result.latitude,
                        result.longitude,
                    );
                    postcode_to_merc_lookup[search_postcode] = merc;
                    update_distances(merc[0], merc[1]);
                });
            } else {
                const merc = postcode_to_merc_lookup[search_postcode];
                update_distances(merc[0], merc[1]);
            }
        } else {
            reset_distances();
        }
    }

    // CSV

    function download_csv() {
        const exclude_cols = ["merc_x", "merc_y", "Type & Rating"];

        let csvContent = "data:text/csv;charset=utf-8,";
        let keys = Object.keys(data[0]);
        keys = keys.filter((key) => !exclude_cols.includes(key));
        csvContent += keys.join(",") + "\n";

        data.forEach((row) => {
            csvContent += keys.map((k) => row[k]).join(",") + "\n";
        });

        // Create a link and trigger download
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "care_visa_sponsors.csv");
        document.body.appendChild(link); // Required for FF

        link.click(); // This will download the file
    }
</script>

<div class="flex flex-col md:flex-row items-end py-4 justify-between">
    <div class="flex flex-col md:flex-row w-full">
        <div class="flex flex-col mb-5 md:mb-0">
            <Label class="mb-2">Search by postcode:</Label>

            <Input
                bind:value={search_postcode}
                class={`${valid_postcode(search_postcode) ? "" : "text-red-500"} uppercase`}
            ></Input>
        </div>

        <div class="flex flex-col md:ml-10 mb-2 md:mb-0">
            <Label class="mb-2">Search by location:</Label>

            <Popover.Root bind:open let:ids>
                <Popover.Trigger asChild let:builder>
                    <Button
                        builders={[builder]}
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        class="w-full md:w-[250px]  justify-between"
                    >
                        {selectedValue}
                        <ChevronsUpDown
                            class="ml-2 h-4 w-4 shrink-0 opacity-50"
                        />
                    </Button>
                </Popover.Trigger>
                <Popover.Content class="p-0 w-full md:w-[250px]">
                    <Command.Root>
                        <Command.Input
                            placeholder="Select location"
                            bind:value={placeFilter}
                        />
                        <Command.Empty>No framework found.</Command.Empty>
                        <Command.Group>
                            {#each filteredPlaces as place (place.value)}
                                <Command.Item
                                    value={place.value}
                                    onSelect={(currentValue) => {
                                        value = currentValue;
                                        closeAndFocusTrigger(ids.trigger);
                                    }}
                                >
                                    <Check
                                        class={cn(
                                            "mr-2 h-4 w-4",
                                            value !== place.value &&
                                                "text-transparent",
                                        )}
                                    />
                                    {place.label}
                                </Command.Item>
                            {/each}
                        </Command.Group>
                    </Command.Root>
                </Popover.Content>
            </Popover.Root>
        </div>
    </div>

    <Input
        class="w-full mt-4 md:mt-0"
        placeholder="Filter organisations"
        type="text"
        bind:value={$filterValue}
    />
</div>

<div class="rounded-md border">
    <Table.Root {...$tableAttrs}>
        <Table.Header>
            {#each $headerRows as headerRow}
                <Subscribe rowAttrs={headerRow.attrs()}>
                    <Table.Row>
                        {#each headerRow.cells as cell (cell.id)}
                            <Subscribe
                                attrs={cell.attrs()}
                                let:attrs
                                props={cell.props()}
                                let:props
                            >
                                <Table.Head {...attrs}>
                                    {#if cell.id === "distance"}
                                        <Button
                                            variant="ghost"
                                            on:click={props.sort.toggle}
                                        >
                                            <Render of={cell.render()} />
                                            <ArrowUpDown
                                                class={"ml-2 h-4 w-4"}
                                            />
                                        </Button>
                                    {:else}
                                        <Render of={cell.render()} />
                                    {/if}
                                </Table.Head>
                            </Subscribe>
                        {/each}
                    </Table.Row>
                </Subscribe>
            {/each}
        </Table.Header>
        <Table.Body {...$tableBodyAttrs}>
            {#each $pageRows as row (row.id)}
                <Subscribe rowAttrs={row.attrs()} let:rowAttrs>
                    <Table.Row {...rowAttrs}>
                        {#each row.cells as cell (cell.id)}
                            <Subscribe attrs={cell.attrs()} let:attrs>
                                <Table.Cell {...attrs}>
                                    {#if cell.id === "Town/City"}
                                        <div class="capitalize">
                                            <Render of={cell.render()} />
                                        </div>
                                    {:else if cell.id === "Organisation Name"}
                                        <a
                                            href="https://www.google.com/search?q={cell.value}"
                                            class="font-medium text-blue-400 hover:underline"
                                            target="_blank"
                                        >
                                            <Render of={cell.render()} />
                                        </a>
                                    {:else if cell.id === "distance"}
                                        <!--
                                        <Render
                                            of={isNaN(parseFloat(cell.value))
                                                ? ""
                                                : parseFloat(
                                                      cell.value,
                                                  ).toFixed(1)}
                                        />
                                        -->

                                        <Render
                                            of={isNaN(parseFloat(cell.value))
                                                ? ""
                                                : formatDistanceAsStr(
                                                      cell.value,
                                                  )}
                                        />
                                    {:else}
                                        <Render of={cell.render()} />
                                    {/if}
                                </Table.Cell>
                            </Subscribe>
                        {/each}
                    </Table.Row>
                </Subscribe>
            {/each}
        </Table.Body>
    </Table.Root>
</div>

<div class="flex flex-col md:flex-row justify-between py-4">
    <Button on:click={download_csv}>Download sponsor list</Button>

    <div>
        <div class="flex items-center justify-center md:justify-end space-x-4 mt-4 md:mt-0">
            <Button
                variant="outline"
                size="sm"
                on:click={() => ($pageIndex = $pageIndex - 1)}
                disabled={!$hasPreviousPage}>Previous</Button
            >

            &nbsp;
            {$pageIndex + 1} out of {$pageCount}

            <Button
                variant="outline"
                size="sm"
                disabled={!$hasNextPage}
                on:click={() => ($pageIndex = $pageIndex + 1)}>Next</Button
            >
        </div>
    </div>
</div>
