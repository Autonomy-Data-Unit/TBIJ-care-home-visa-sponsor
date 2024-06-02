<script lang="ts">
    import DataTable from "./data-table.svelte";
    import { onMount } from "svelte";
    import { base } from "$app/paths";
    import * as d3 from "d3";
    import { Skeleton } from "$lib/components/ui/skeleton";
    //import { last_updated } from "$lib/last_updated.ts";


    let data = [];
    let place_merc_lookup;
    let isLoaded = false;
    var last_updated;

    onMount(async () => {
        data = await d3.csv(`${base}/sponsors.csv`);
        const response = await fetch(`${base}/place_merc_lookup.json`);
        place_merc_lookup = await response.json();
        isLoaded = true;

        // Load last_updated.txt
        const lastUpdatedResponse = await fetch(`${base}/last_updated.txt`);
        last_updated = await lastUpdatedResponse.text();

        isLoaded = true;

        /*
        setTimeout(async () => {
            isLoaded = true;
        }, 2000);*/
    });
</script>

<div class="container mx-auto py-10 font-sans">
    {#if isLoaded}
    <div class="mb-2">
        <small>Last updated on: {last_updated}</small>
    </div>

        <DataTable {data} {place_merc_lookup} />
    {:else}
        {#each Array.from({ length: 15 }) as _, index}
            <Skeleton class="h-[1rem] w-[80pc] mb-5 rounded-full" />
        {/each}
    {/if}
</div>
