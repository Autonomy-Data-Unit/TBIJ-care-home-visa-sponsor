<script lang="ts">
    import { onMount } from "svelte";
    import * as d3 from "d3";

    type Payment = {
        id: string;
        amount: number;
        status: "pending" | "processing" | "success" | "failed";
        email: string;
    };

    let data = [];

    onMount(async () => {
        const data = await d3.csv("/static/sponsors.csv");
    });
</script>
