cd care-sponsors-svelte-app
rm -rf build
npm run build

cd ..
rm -rf app
cp -r care-sponsors-svelte-app/build app