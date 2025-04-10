import Layout from "@/components/Layout.tsx";
import RedBookLogin from "@/components/RedBookLogin.tsx";

const Platform = () => {

  return (
    <Layout>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RedBookLogin/>
      </div>
    </Layout>
);
};

export default Platform;
